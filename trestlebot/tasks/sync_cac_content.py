# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import json
import logging
import os
from typing import Any, Dict, List

from ssg import build_yaml
from ssg.build_profile import make_name_to_profile_mapping
from ssg.controls import ControlsManager
from ssg.entities.profile import ProfileWithInlinePolicies
from ssg.environment import open_environment
from ssg.products import (
    get_profile_files_from_root,
    load_product_yaml,
    product_yaml_path,
)
from ssg.rules import get_rule_dir_yaml
from trestle.common.list_utils import none_if_empty
from trestle.core.generators import generate_sample_model
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition, DefinedComponent

from trestlebot import const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transform import RuleInfo, RulesTransformer


logger = logging.getLogger(__name__)


def get_env_yaml(cac_content_root: str, product: str) -> Dict[str, Any]:
    """Get the environment yaml."""
    build_config_yaml = os.path.join(cac_content_root, "build", "build_config.yml")
    product_yml_path = product_yaml_path(cac_content_root, product)
    env_yaml = open_environment(
        build_config_yaml,
        product_yml_path,
        os.path.join(cac_content_root, "product_properties"),
    )
    return env_yaml


class SyncCaCContentTask(TaskBase):
    """
    Sync CaC content to OSCAL component definition task.
    """

    def __init__(
        self,
        product: str,
        cac_profile: str,
        cac_content_root: str,
        component_definition_type: str,
        oscal_profile: str,
        working_dir: str,
    ) -> None:
        """
        Initialize CaC content sync task.
        """

        self.product: str = product
        self.cac_profile: str = cac_profile
        self.cac_content_root: str = cac_content_root
        self.component_definition_type: str = component_definition_type
        self.rules_json_path: str = ""
        self.env_yaml: Dict[str, Any] = {}
        self.selected: List[str] = []
        self.variables: Dict[str, Any] = {}

        super().__init__(working_dir, None)

    def _collect_rules(self) -> None:
        """
        Collect all rules from the product profile.

        Returns:
         0 on success, raises an exception if not successful
        """

        env_yaml = get_env_yaml(self.cac_content_root, self.product)
        # profile = ProfileWithInlinePolicies.from_yaml(self.cac_profile, env_yaml)
        # When run with env_yaml, error:
        # AttributeError: 'NoneType' object has no attribute 'get_cpe_name'
        # Here the JINJA_MACROS_DIRECTORY can not be found.
        # Workaround is to update it in ssg constants.
        profile = ProfileWithInlinePolicies.from_yaml(self.cac_profile)

        control_manager = ControlsManager(
            os.path.join(self.cac_content_root, "controls"), env_yaml
        )
        control_manager.load()

        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)
        profile_files = get_profile_files_from_root(env_yaml, product_data)
        # all_profiles = make_name_to_profile_mapping(profile_files, env_yaml, product_cpes)
        # Where to get the product_cpes?
        # Here if set env_yaml without product_cpes, will raise error like:
        # Error loading a ProfileWithInlinePolicies from
        # /cac_content_root/products/ocp4/profiles/bsi-2022.profile:
        # 'NoneType' object has no attribute 'get_cpe_name'
        all_profiles = make_name_to_profile_mapping(profile_files, None, None)

        # rule_dirs.json is from utils/rule_dir_json.py
        # The way to get the data should be updatd.
        self.rules_json_path = os.path.join(
            self.cac_content_root, "build", "rule_dirs.json"
        )
        rules_json = open(self.rules_json_path, "r")

        all_rules = json.load(rules_json)
        # There is an error in running apply_filter with all_rules
        # Here needs an update in all_rules:
        # from {rule_id: rule_dict} to {rule_id: rule_obj}
        # e.g. update rules_by_id.get("service_com_apple_auditd_enabled") from dict:
        # {
        #     'id': 'service_com_apple_auditd_enabled',
        #     'dir': '/home/qduanmu/projects/content/apple_os/auditing/service_com_apple_auditd_enabled',
        #     ...
        # }
        # to rule object:
        # ssg.build_yaml.Rule object
        rule_objs_by_id = {}
        for k, v in all_rules.items():
            rule_file = get_rule_dir_yaml(v["dir"])
            rule_obj = build_yaml.Rule.from_yaml(rule_file, env_yaml)
            rule_objs_by_id.update({k: rule_obj})
        profile.resolve(all_profiles, rule_objs_by_id, control_manager)
        if not rules_json.closed:
            rules_json.close()

        # Example of profile.selected:
        # [
        #     'accounts_restrict_service_account_tokens',
        #     'accounts_unique_service_account',
        #     ...
        #     'version_detect_in_ocp'
        # ]
        # Example of profile.variables:
        # {
        #     'var_event_record_qps': '50',
        #     'var_openshift_audit_profile': 'WriteRequestBodies',
        #     'var_oauth_inactivity_timeout': '10m0s'
        #  }
        self.selected = profile.selected
        self.variables = profile.variables
        self.env_yaml = env_yaml

    def create_compdef(self, component_definition_type: str = "service") -> None:
        """Create a component definition for specified product."""

        logger.info(f"Creating component definition for {self.product}")
        # Need to switch to trestlebot AuthoredComponentDefinition
        component_definition = generate_sample_model(ComponentDefinition)
        component_definition.metadata.title = f"Component definition for {self.product}"
        component_definition.components = list()

        oscal_component = generate_sample_model(DefinedComponent)
        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)
        oscal_component.title = product_data._primary_data.get("product")
        oscal_component.type = component_definition_type
        oscal_component.description = self.product

        rules_transformer = RulesTransformer(
            self.cac_content_root,
            self.env_yaml,
            self.rules_json_path,
            # self.params_extractor
        )
        # Create all of the top-level component properties for rules
        rules_transformer.add_rules(self.selected)
        rules: List[RuleInfo] = rules_transformer.get_all_rules()
        all_rule_properties: List[Property] = rules_transformer.transform(rules)
        oscal_component.props = none_if_empty(all_rule_properties)
        component_definition.components.append(oscal_component)

    def execute(self) -> int:
        """Execute task"""

        # Collect all product rules selected in profile.
        self._collect_rules()
        # Add rules to component definition pro
        self.create_compdef()
        return const.SUCCESS_EXIT_CODE

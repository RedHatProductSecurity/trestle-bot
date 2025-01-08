# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import json
import logging
import os
import pathlib
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
from trestle.common import const as trestle_const
from trestle.common.list_utils import none_if_empty
from trestle.core.generators import generate_sample_model
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition, DefinedComponent

from trestlebot import const
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    RuleInfo,
    RulesTransformer,
    get_component_info,
    update_component_definition,
)


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


class SyncCacContentTask(TaskBase):
    """
    Sync CaC content to OSCAL component definition task.
    """

    def __init__(
        self,
        product: str,
        cac_profile: str,
        cac_content_root: str,
        compdef_type: str,
        oscal_profile: str,
        authored_object: AuthoredObjectBase,
    ) -> None:
        """
        Initialize CaC content sync task.
        """

        self.product: str = product
        self.cac_profile: str = cac_profile
        self.cac_content_root: str = cac_content_root
        self.compdef_type: str = compdef_type
        self.rules_json_path: str = ""
        self.env_yaml: Dict[str, Any] = {}
        self.selected: List[str] = []

        self._authored_object = authored_object
        working_dir = self._authored_object.get_trestle_root()
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
        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)

        control_manager = ControlsManager(
            os.path.join(self.cac_content_root, "controls"), product_data
        )
        control_manager.load()

        profile_files = get_profile_files_from_root(product_data, product_data)
        # all_profiles = make_name_to_profile_mapping(profile_files, env_yaml, product_cpes)
        # Where to get the product_cpes?
        # Here if set env_yaml without setting product_cpes, will raise error like:
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
        #     'dir': '/cac_content_root/apple_os/auditing/service_com_apple_auditd_enabled',
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
        self.env_yaml = env_yaml

    def _create_or_update_compdef(self, compdef_type: str = "service") -> None:
        """Create a component definition for specified product."""

        component_definition = generate_sample_model(ComponentDefinition)
        component_definition.metadata.title = f"Component definition for {self.product}"
        component_definition.metadata.version = "1.0"
        component_definition.components = list()

        oscal_component = generate_sample_model(DefinedComponent)
        product_name, full_name = get_component_info(
            self.product, self.cac_content_root
        )
        oscal_component.title = product_name
        oscal_component.type = compdef_type
        oscal_component.description = full_name

        rules_transformer = RulesTransformer(
            self.cac_content_root,
            self.env_yaml,
            self.rules_json_path,
        )
        # Create all of the top-level component properties for rules
        rules_transformer.add_rules(self.selected)
        rules: List[RuleInfo] = rules_transformer.get_all_rules()
        all_rule_properties: List[Property] = rules_transformer.transform(rules)
        oscal_component.props = none_if_empty(all_rule_properties)

        repo_path = pathlib.Path(self.working_dir)
        cd_dir = repo_path.joinpath(f"{trestle_const.MODEL_DIR_COMPDEF}/{self.product}")
        cd_json = cd_dir / "component-definition.json"
        if cd_json.exists():
            logger.info(f"The component definition for {self.product} exists.")
            with open(cd_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                components = data["component-definition"]["components"]
            for index, component in enumerate(components):
                if component.get("title") == oscal_component.title:
                    # The update should be skipped if no content changes
                    logger.info(f"Update props of component {product_name}")
                    data["component-definition"]["components"][index][
                        "props"
                    ] = oscal_component.props
                    update_component_definition(cd_json)
        else:
            logger.info(f"Creating component definition for product {self.product}")
            cd_dir.mkdir(exist_ok=True, parents=True)
            cd_json = cd_dir / "component-definition.json"
            component_definition.components.append(oscal_component)
            component_definition.oscal_write(cd_json)

    def execute(self) -> int:
        """Execute task to create or update product component definition."""

        # Collect all product rules selected in product profile
        self._collect_rules()
        # Create or update product component definition
        self._create_or_update_compdef()
        return const.SUCCESS_EXIT_CODE

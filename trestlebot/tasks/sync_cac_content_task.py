# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import datetime
import logging
import os
import pathlib
from typing import List

# from ssg.products import get_all
from ssg.profiles import get_profiles_from_products
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
)


logger = logging.getLogger(__name__)


class SyncCacContentTask(TaskBase):
    """Sync CaC content to OSCAL component definition task."""

    def __init__(
        self,
        product: str,
        cac_profile: str,
        cac_content_root: str,
        compdef_type: str,
        oscal_profile: str,
        authored_object: AuthoredObjectBase,
    ) -> None:
        """Initialize CaC content sync task."""
        self.product: str = product
        self.cac_profile: str = cac_profile
        self.cac_content_root: str = cac_content_root
        self.compdef_type: str = compdef_type
        self.rules: List[str] = []

        self._authored_object = authored_object
        working_dir = self._authored_object.get_trestle_root()
        super().__init__(working_dir, None)

    def _collect_rules(self) -> None:
        """Collect all rules from the product profile."""
        profiles = get_profiles_from_products(self.cac_content_root, [self.product])
        cac_profile_id = os.path.basename(self.cac_profile).split(".profile")[0]
        for profile in profiles:
            if profile.profile_id == cac_profile_id:
                self.rules = profile.rules
                break

    def _get_rules_properties(self) -> List[Property]:
        """Create all of the top-level component properties for rules."""
        rules_transformer = RulesTransformer(
            self.cac_content_root,
            self.product,
        )
        rules_transformer.add_rules(self.rules)
        rules: List[RuleInfo] = rules_transformer.get_all_rules()
        all_rule_properties: List[Property] = rules_transformer.transform(rules)
        return all_rule_properties

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
        all_rule_properties = self._get_rules_properties()
        oscal_component.props = none_if_empty(all_rule_properties)

        repo_path = pathlib.Path(self.working_dir)
        cd_dir = repo_path.joinpath(f"{trestle_const.MODEL_DIR_COMPDEF}/{self.product}")
        cd_json = cd_dir / "component-definition.json"
        if cd_json.exists():
            logger.info(f"The component definition for {self.product} exists.")
            compdef = ComponentDefinition.oscal_read(cd_json)
            updated = False
            for index, component in enumerate(compdef.components):
                if component.title == oscal_component.title:
                    if component.props != oscal_component.props:
                        compdef.components[index].props = oscal_component.props
                        updated = True
                        break
            if updated:
                logger.info(f"Update component definition: {cd_json}")
                compdef.metadata.version = str(
                    "{:.1f}".format(float(compdef.metadata.version) + 0.1)
                )
                compdef.metadata.last_modified = (
                    datetime.datetime.now(datetime.timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                )
                compdef.oscal_write(cd_json)
        else:
            logger.info(f"Creating component definition for product {self.product}")
            cd_dir.mkdir(exist_ok=True, parents=True)
            cd_json = cd_dir / "component-definition.json"
            component_definition.components.append(oscal_component)
            component_definition.oscal_write(cd_json)

    def execute(self) -> int:
        """Execute task to create or update product component definition."""
        # Check the product existence in CaC content.
        # Comment below due to the hardcoded product_directories in get_all,
        # all_products = list(set().union(*get_all(self.cac_content_root)))
        # if self.product not in all_products:
        #     raise TaskException(f"Product {self.product} does not exist.")
        # Collect all selected rules in product profile
        self._collect_rules()
        # Create or update product component definition
        self._create_or_update_compdef()
        return const.SUCCESS_EXIT_CODE

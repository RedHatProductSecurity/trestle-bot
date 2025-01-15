# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import logging
import os
import pathlib
from typing import List

# from ssg.products import get_all
from ssg.profiles import get_profiles_from_products
from trestle.common.list_utils import none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.generators import generate_sample_model
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition, DefinedComponent

from trestlebot import const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    RuleInfo,
    RulesTransformer,
    get_component_info,
    get_validation_component_mapping,
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
        working_dir: str,
    ) -> None:
        """Initialize CaC content sync task."""
        self.product: str = product
        self.cac_profile: str = cac_profile
        self.cac_content_root: str = cac_content_root
        self.compdef_type: str = compdef_type
        self.rules: List[str] = []

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
            self.cac_profile,
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
        all_rule_properties = self._get_rules_properties()
        props = none_if_empty(all_rule_properties)
        oscal_component.type = self.compdef_type
        if oscal_component.type == "validation":
            oscal_component.title = "openscap"
            oscal_component.description = "openscap"
            oscal_component.props = get_validation_component_mapping(props)
        else:
            oscal_component.title = product_name
            oscal_component.description = full_name
            oscal_component.props = props
        repo_path = pathlib.Path(self.working_dir)
        cd_json: pathlib.Path = ModelUtils.get_model_path_for_name_and_class(
            repo_path,
            self.product,
            ComponentDefinition,
            FileContentType.JSON,
        )

        if cd_json.exists():
            logger.info(f"The component definition for {self.product} exists.")
            compdef = ComponentDefinition.oscal_read(cd_json)
            components_titles = []
            updated = False
            for index, component in enumerate(compdef.components):
                components_titles.append(component.title)
                # If the component exists and the props need to be updated
                if component.title == oscal_component.title:
                    if component.props != oscal_component.props:
                        logger.info(
                            f"Start to update props of the component {component.title}"
                        )
                        compdef.components[index].props = oscal_component.props
                        updated = True
                        compdef.oscal_write(cd_json)
                        break
            if oscal_component.title not in components_titles:
                logger.info(f"Start to append component {oscal_component.title}")
                compdef.components.append(oscal_component)
                compdef.oscal_write(cd_json)
                updated = True
            if updated:
                logger.info(f"Update component definition: {cd_json}")
                compdef.metadata.version = str(
                    "{:.1f}".format(float(compdef.metadata.version) + 0.1)
                )
                ModelUtils.update_last_modified(compdef)
                compdef.oscal_write(cd_json)
        else:
            logger.info(f"Creating component definition for product {self.product}")
            cd_dir = pathlib.Path(os.path.dirname(cd_json))
            cd_dir.mkdir(exist_ok=True, parents=True)
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

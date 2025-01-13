# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Trestle Bot Sync CaC Content Tasks"""

import datetime
import logging
import pathlib
from typing import Any, Dict, List

import trestle.common.const as com_const
from trestle.core.generators import generate_sample_model
from trestle.oscal.component import ComponentDefinition, DefinedComponent

from trestlebot import const
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    get_component_info,
    get_validation_component_mapping,
)


logger = logging.getLogger(__name__)


class SyncCacContentTask(TaskBase):
    """
    Sync CaC content to OSCAL component definition task.
    """

    def __init__(
        self,
        product: str,
        cac_profile: str,
        cac_content_root: str,
        comp_type: str,
        oscal_profile: str,
        authored_object: AuthoredObjectBase,
    ) -> None:
        """
        Initialize CaC content sync task.
        """
        self.product: str = product
        self.cac_profile: str = cac_profile
        self.cac_content_root: str = cac_content_root
        self.comp_type: str = comp_type
        self.rules_json_path: str = ""
        self.env_yaml: Dict[str, Any] = {}
        self.selected: List[str] = []

        self._authored_object = authored_object
        working_dir = self._authored_object.get_trestle_root()
        super().__init__(working_dir, None)

    def _create_or_update_compdef(self, comp_type: str = "service") -> None:
        """Create or update a component definition for specified product."""

        component_definition = generate_sample_model(ComponentDefinition)
        component_definition.metadata.title = f"Component definition for {self.product}"
        component_definition.metadata.version = "1.0"
        component_definition.components = list()

        oscal_component = generate_sample_model(DefinedComponent)
        product_name, full_name = get_component_info(
            self.product, self.cac_content_root
        )
        # Collect rules and parameters as the props will be updated in CPLYTM-218
        # rules_transformer.add_rules(self.selected)
        # rules: List[RuleInfo] = rules_transformer.get_all_rules()
        # all_rule_properties: List[Property] = rules_transformer.transform(rules)
        # props = none_if_empty(all_rule_properties)
        # Assumption of having obtained the rules as follows
        props = [
            {
                "name": "Rule_Id",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/cd",
                "value": "file_permissions_kube_apiserver",
                "remarks": "rule_set_201",
            },
            {
                "name": "Rule_Description",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/cd",
                "value": "Ensure",
                "remarks": "rule_set_201",
            },
            {
                "name": "Rule_Id",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/cd",
                "value": "file_owner_kube_apiserver",
                "remarks": "rule_set_202",
            },
            {
                "name": "Rule_Description",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/cd",
                "value": "Ensure",
                "remarks": "rule_set_202",
            },
        ]
        oscal_component.type = self.comp_type
        if oscal_component.type == "validation":
            oscal_component.title = "openscap"
            oscal_component.description = "openscap"
            oscal_component.props = get_validation_component_mapping(props)
        else:
            oscal_component.title = product_name
            oscal_component.description = full_name
            oscal_component.props = props
        repo_path = pathlib.Path(self.working_dir)
        cd_dir = repo_path.joinpath(f"{com_const.MODEL_DIR_COMPDEF}/{self.product}")
        cd_json = cd_dir / "component-definition.json"
        if cd_json.exists():
            logger.info(f"The component definition for product {self.product} exists.")
            compdef = ComponentDefinition.oscal_read(cd_json)
            components_titles = []
            updated = False
            for index, component in enumerate(compdef.components):
                components_titles.append(component.title)
                # If the component exists and the props need to be updated
                if component.title == oscal_component.title:
                    if component.props != oscal_component.props:
                        logger.info(
                            f"Start to update the props of the component {component.title}"
                        )
                        compdef.components[index].props = oscal_component.props
                        updated = True
                        compdef.oscal_write(cd_json)
                        break
            # If the component doesn't exist, append this component
            if oscal_component.title not in components_titles:
                logger.info(f"{oscal_component.title}")
                logger.info(f"Start to append the component {oscal_component.title}")
                compdef.components.append(oscal_component)
                compdef.oscal_write(cd_json)
                updated = True
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

        # Collect all product rules selected in product profile
        # self._collect_rules()
        # Create or update product component definition
        self._create_or_update_compdef()
        return const.SUCCESS_EXIT_CODE

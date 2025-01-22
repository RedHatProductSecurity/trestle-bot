# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import logging
import os
import pathlib
import re
from typing import Dict, List, Optional, Pattern, Set

# from ssg.products import get_all
from ssg.controls import Control, ControlsManager
from ssg.products import load_product_yaml, product_yaml_path
from ssg.profiles import _load_yaml_profile_file, get_profiles_from_products
from trestle.common.common_types import TypeWithParts, TypeWithProps
from trestle.common.const import TRESTLE_HREF_HEADING
from trestle.common.list_utils import as_list, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_interface import ControlInterface
from trestle.core.generators import generate_sample_model
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Property
from trestle.oscal.component import (
    ComponentDefinition,
    ControlImplementation,
    DefinedComponent,
    ImplementedRequirement,
    SetParameter,
    Statement,
)

from trestlebot import const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    RuleInfo,
    RulesTransformer,
    get_component_info,
    get_validation_component_mapping,
)


logger = logging.getLogger(__name__)

SECTION_PATTERN = r"Section ([a-z]):"


class OSCALProfileHelper:
    """Helper class to handle OSCAL profile."""

    def __init__(self, trestle_root: pathlib.Path) -> None:
        """Initialize."""
        self._root = trestle_root
        self.profile_controls: Set[str] = set()
        self.controls_by_label: Dict[str, str] = dict()

    def load(self, profile_path: str) -> None:
        """Load the profile catalog."""
        profile_resolver = ProfileResolver()
        resolved_catalog: Catalog = profile_resolver.get_resolved_profile_catalog(
            self._root,
            profile_path,
            block_params=False,
            params_format="[.]",
            show_value_warnings=True,
        )

        for control in CatalogInterface(resolved_catalog).get_all_controls_from_dict():
            self.profile_controls.add(control.id)
            label = ControlInterface.get_label(control)
            if label:
                self.controls_by_label[label] = control.id
                self._handle_parts(control)

    def _handle_parts(
        self,
        control: TypeWithParts,
    ) -> None:
        """Handle parts of a control."""
        if control.parts:
            for part in control.parts:
                if not part.id:
                    continue
                self.profile_controls.add(part.id)
                label = ControlInterface.get_label(part)
                # Avoiding key collision here. The higher level control object will take
                # precedence.
                if label and label not in self.controls_by_label.keys():
                    self.controls_by_label[label] = part.id
                self._handle_parts(part)

    def validate(self, control_id: str) -> Optional[str]:
        """Validate that the control id exists in the catalog and return the id"""
        if control_id in self.controls_by_label.keys():
            logger.debug(f"Found control {control_id} in control labels")
            return self.controls_by_label.get(control_id)
        elif control_id in self.profile_controls:
            logger.debug(f"Found control {control_id} in profile control ids")
            return control_id

        logger.debug(f"Control {control_id} does not exist in the profile")
        return None


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
        self.oscal_profile: str = oscal_profile
        self.rules: List[str] = []
        self.controls: List[Control] = list()
        self.rules_by_id: Dict[str, RuleInfo] = dict()

        self.profile_href: str = ""
        self.profile_path: str = ""
        self.profile = OSCALProfileHelper(pathlib.Path(working_dir))

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
        self.rules_by_id = rules_transformer.get_all_rule_objs()
        rules: List[RuleInfo] = list(self.rules_by_id.values())
        all_rule_properties: List[Property] = rules_transformer.transform(rules)
        return all_rule_properties

    def _add_props(self, oscal_component: DefinedComponent) -> DefinedComponent:
        """Add props to OSCAL component."""
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
        return oscal_component

    def _get_source(self, profile_name_or_href: str) -> None:
        """Get the href and source of the profile."""
        profile_in_trestle_dir = "://" not in profile_name_or_href
        self.profile_href = profile_name_or_href
        if profile_in_trestle_dir:
            local_path = f"profiles/{profile_name_or_href}/profile.json"
            self.profile_href = TRESTLE_HREF_HEADING + local_path
            self.profile_path = os.path.join(self.working_dir, local_path)
        else:
            self.profile_path = self.profile_href

    def _load_controls_manager(self) -> ControlsManager:
        """
        Loads and initializes a ControlsManager instance.
        """
        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_yaml = load_product_yaml(product_yml_path)
        controls_dir = os.path.join(self.cac_content_root, "controls")
        control_mgr = ControlsManager(controls_dir, product_yaml)
        control_mgr.load()
        return control_mgr

    def _get_controls(self) -> None:
        """Collect controls selected by profile."""
        controls_manager = self._load_controls_manager()
        policies = controls_manager.policies
        profile_yaml = _load_yaml_profile_file(self.cac_profile)
        selections = profile_yaml.get("selections", [])
        for selected in selections:
            if ":" in selected:
                parts = selected.split(":")
                if len(parts) == 3:
                    policy_id, level = parts[0], parts[2]
                else:
                    policy_id, level = parts[0], "all"
                policy = policies.get(policy_id)
                if policy is not None:
                    self.controls.extend(
                        controls_manager.get_all_controls_of_level(policy_id, level)
                    )

    @staticmethod
    def _build_sections_dict(
        control_response: str,
        section_pattern: Pattern[str],
    ) -> Dict[str, List[str]]:
        """Find all sections in the control response and build a dictionary of them."""
        lines = control_response.split("\n")

        sections_dict: Dict[str, List[str]] = dict()
        current_section_label = None

        for line in lines:
            match = section_pattern.match(line)

            if match:
                current_section_label = match.group(1)
                sections_dict[current_section_label] = [line]
            elif current_section_label is not None:
                sections_dict[current_section_label].append(line)

        return sections_dict

    def _create_statement(self, statement_id: str, description: str = "") -> Statement:
        """Create a statement."""
        statement = generate_sample_model(Statement)
        statement.statement_id = statement_id
        if description:
            statement.description = description
        return statement

    def _handle_response(
        self,
        implemented_req: ImplementedRequirement,
        control: Control,
    ) -> None:
        """
        Break down the response into parts.

        Args:
            implemented_req: The implemented requirement to add the response and statements to.
            control_response: The control response to add to the implemented requirement.
        """
        # If control notes is unavailable, consider to use other input as replacement
        # or a generic information.
        control_response = control.notes
        pattern = re.compile(SECTION_PATTERN, re.IGNORECASE)

        sections_dict = self._build_sections_dict(control_response, pattern)
        # oscal_status = OscalStatus.from_string(control.status)

        if sections_dict:
            # self._add_response_by_status(implemented_req, oscal_status, REPLACE_ME)
            implemented_req.statements = list()
            for section_label, section_content in sections_dict.items():
                statement_id = self.profile.validate(
                    f"{implemented_req.control_id}_smt.{section_label}"
                )
                if statement_id is None:
                    continue

                section_content_str = "\n".join(section_content)
                section_content_str = pattern.sub("", section_content_str)
                statement = self._create_statement(
                    statement_id, section_content_str.strip()
                )
                implemented_req.statements.append(statement)
        # else:
        #     self._add_response_by_status(
        #         implemented_req, oscal_status, control_response.strip()
        #     )

    def _process_rule_ids(self, rule_ids: List[str]) -> List[str]:
        """
        Process rule ids.
        Notes: Rule ids with an "=" are parameters and should not be included
        # when searching for rules.
        """
        processed_rule_ids: List[str] = list()
        for rule_id in rule_ids:
            parts = rule_id.split("=")
            if len(parts) == 1:
                processed_rule_ids.append(rule_id)
        return processed_rule_ids

    def _attach_rules(
        self,
        type_with_props: TypeWithProps,
        rule_ids: List[str],
        rules_transformer: RulesTransformer,
    ) -> None:
        """Add rules to a type with props."""
        all_props: List[Property] = as_list(type_with_props.props)
        all_rule_ids = self.rules_by_id.keys()
        error_rules = list(filter(lambda x: x not in all_rule_ids, rule_ids))
        if error_rules:
            raise ValueError(f"Could not find rules: {', '.join(error_rules)}")
        rule_properties: List[Property] = rules_transformer.get_rule_id_props(rule_ids)
        all_props.extend(rule_properties)
        type_with_props.props = none_if_empty(all_props)

    def _add_set_parameters(
        self, control_implementation: ControlImplementation
    ) -> None:
        """Add set parameters to a control implementation."""
        rules: List[RuleInfo] = list(self.rules_by_id.values())
        params = []
        for rule in rules:
            params.extend(rule._parameters)
        param_selections = {param.id: param.selected_value for param in params}

        if param_selections:
            all_set_params: List[SetParameter] = as_list(
                control_implementation.set_parameters
            )
            for param_id, value in param_selections.items():
                set_param = generate_sample_model(SetParameter)
                set_param.param_id = param_id
                set_param.values = [value]
                all_set_params.append(set_param)
            control_implementation.set_parameters = none_if_empty(all_set_params)

    def _create_implemented_requirement(
        self, control: Control, rules_transformer: RulesTransformer
    ) -> Optional[ImplementedRequirement]:
        """Create implemented requirement from a control object"""

        logger.info(f"Creating implemented requirement for {control.id}")
        control_id = self.profile.validate(control.id)
        if control_id:
            implemented_req = generate_sample_model(ImplementedRequirement)
            implemented_req.control_id = control_id
            self._handle_response(implemented_req, control)
            rule_ids = self._process_rule_ids(control.rules)
            self._attach_rules(implemented_req, rule_ids, rules_transformer)
            return implemented_req
        return None

    def _create_control_implementation(self) -> ControlImplementation:
        """Create control implementation for a component."""
        ci = generate_sample_model(ControlImplementation)
        ci.source = self.profile_href
        all_implement_reqs = list()
        self._get_controls()
        rules_transformer = RulesTransformer(
            self.cac_content_root,
            self.product,
            self.cac_profile,
        )

        for control in self.controls:
            implemented_req = self._create_implemented_requirement(
                control, rules_transformer
            )
            if implemented_req:
                all_implement_reqs.append(implemented_req)
        ci.implemented_requirements = all_implement_reqs
        self._add_set_parameters(ci)
        return ci

    def _add_control_implementations(
        self, oscal_component: DefinedComponent
    ) -> DefinedComponent:
        """Add control implementations to OSCAL component."""
        self._get_source(self.oscal_profile)
        self.profile.load(self.profile_path)
        control_implementation: ControlImplementation = (
            self._create_control_implementation()
        )
        oscal_component.control_implementations = [control_implementation]
        return oscal_component

    def _update_compdef(
        self, cd_json: pathlib.Path, oscal_component: DefinedComponent
    ) -> None:
        """Update existed OSCAL component definition."""
        compdef = ComponentDefinition.oscal_read(cd_json)
        components_titles = []
        updated = False
        for index, component in enumerate(compdef.components):
            components_titles.append(component.title)
            # If the component exists and the props need to be updated
            if component.title == oscal_component.title:
                if component.props != oscal_component.props:
                    logger.info(f"Start to update props of {component.title}")
                    compdef.components[index].props = oscal_component.props
                    updated = True
                # The way to check control implementations needs to be updated
                if (
                    component.control_implementations
                    != oscal_component.control_implementations
                ):
                    logger.info(
                        f"Start to update control implementations of {component.title}"
                    )
                    compdef.components[index].control_implementations = (
                        oscal_component.control_implementations
                    )
                    updated = True
                if updated:
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

    def _create_compdef(
        self, cd_json: pathlib.Path, oscal_component: DefinedComponent
    ) -> None:
        """Create a component definition in OSCAL."""
        component_definition = generate_sample_model(ComponentDefinition)
        component_definition.metadata.title = f"Component definition for {self.product}"
        component_definition.metadata.version = "1.0"
        component_definition.components = list()
        cd_dir = pathlib.Path(os.path.dirname(cd_json))
        cd_dir.mkdir(exist_ok=True, parents=True)
        component_definition.components.append(oscal_component)
        component_definition.oscal_write(cd_json)

    def _create_or_update_compdef(self) -> None:
        """Create or update component definition for specified CaC profile."""
        oscal_component = generate_sample_model(DefinedComponent)
        oscal_component = self._add_props(oscal_component)
        oscal_component = self._add_control_implementations(oscal_component)

        repo_path = pathlib.Path(self.working_dir)
        cd_json: pathlib.Path = ModelUtils.get_model_path_for_name_and_class(
            repo_path,
            self.product,
            ComponentDefinition,
            FileContentType.JSON,
        )
        if cd_json.exists():
            logger.info(f"The component definition for {self.product} exists.")
            self._update_compdef(cd_json, oscal_component)
        else:
            logger.info(f"Creating component definition for product {self.product}")
            self._create_compdef(cd_json, oscal_component)

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

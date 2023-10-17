#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Trestle Bot functions for component definition authoring"""

import os
import pathlib
from typing import List

import trestle.common.const as const
import trestle.oscal.profile as prof
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.repository import AgileAuthoring

from trestlebot.const import RULES_VIEW_DIR, YAML_EXTENSION
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Profile,
    TrestleRule,
)
from trestlebot.transformers.yaml_transformer import FromRulesYAMLTransformer


class AuthoredComponentDefinition(AuthorObjectBase):
    """
    Class for authoring OSCAL Component Definitions in automation
    """

    def __init__(self, trestle_root: str) -> None:
        """
        Initialize authored component definitions object.
        """
        super().__init__(trestle_root)

    def assemble(self, markdown_path: str, version_tag: str = "") -> None:
        """Run assemble actions for compdef type at the provided path"""
        trestle_root = pathlib.Path(self.get_trestle_root())
        compdef = os.path.basename(markdown_path)

        authoring = AgileAuthoring(trestle_root)
        try:
            success = authoring.assemble_component_definition_markdown(
                name=compdef,
                output=compdef,
                markdown_dir=markdown_path,
                regenerate=False,
                version=version_tag,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {compdef}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {compdef}: {e}")

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        """Run assemble actions for compdef type at the provided path"""
        trestle_root = pathlib.Path(self.get_trestle_root())
        authoring = AgileAuthoring(trestle_root)

        comp_name = os.path.basename(model_path)

        try:
            success = authoring.generate_component_definition_markdown(
                name=comp_name,
                output=os.path.join(markdown_path, comp_name),
                force_overwrite=False,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while regenerating {comp_name}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(
                f"Trestle generate failed for {comp_name}: {e}"
            )

    def create_new_default(
        self,
        profile_name: str,
        compdef_name: str,
        comp_title: str,
        comp_description: str,
        comp_type: str,
    ) -> None:
        """
        Create the new component definition with default info.

        Args:
            profile_name: Name of the profile to use for the component definition
            compdef_name: Name of the component definition
            comp_title: Title of the component
            comp_description: Description of the component
            comp_type: Type of the component

        Notes:
            The beginning of the Component Definition workflow is to create a new
            rules view. After completed the rules view transformation task can be used for management.
        """
        trestle_root: pathlib.Path = pathlib.Path(self.get_trestle_root())

        existing_profile_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, profile_name, prof.Profile
        )

        if existing_profile_path is None:
            raise AuthoredObjectException(
                f"Profile {profile_name} does not exist in the workspace"
            )

        rule_dir: pathlib.Path = trestle_root.joinpath(RULES_VIEW_DIR, compdef_name)
        rule_dir.parent.mkdir(parents=True, exist_ok=True)

        component_info: ComponentInfo = ComponentInfo(
            name=comp_title, description=comp_description, type=comp_type
        )

        rules_view_builder = RulesViewBuilder(trestle_root)
        rules_view_builder.add_rules_for_profile(existing_profile_path, component_info)
        rules_view_builder.write_to_yaml(rule_dir)


class RulesViewBuilder:
    """Write TrestleRule objects to YAML files in rules view."""

    def __init__(self, trestle_root: pathlib.Path) -> None:
        """Initialize."""
        self._trestle_root = trestle_root
        self._rules: List[TrestleRule] = []
        self._yaml_transformer = FromRulesYAMLTransformer()

    def add_rules_for_profile(
        self, profile_path: pathlib.Path, component_info: ComponentInfo
    ) -> None:
        """Add rules for a profile to the builder."""
        catalog = ProfileResolver.get_resolved_profile_catalog(
            self._trestle_root, profile_path=profile_path
        )

        controls = CatalogInterface.get_control_ids_from_catalog(catalog)

        for control_id in controls:
            rule = TrestleRule(
                component=component_info,
                name=f"rule-{control_id}",
                description=f"Rule for {control_id}",
                profile=Profile(
                    href=const.TRESTLE_HREF_HEADING
                    + str(profile_path.relative_to(self._trestle_root)),
                    description=catalog.metadata.title,
                    include_controls=[Control(id=control_id)],
                ),
            )
            self.add_rule(rule)

    def add_rule(self, rule: TrestleRule) -> None:
        """Add a rule to the builder."""
        self._rules.append(rule)

    def write_to_yaml(self, compdef_path: pathlib.Path) -> None:
        """Write the rules to YAML files in the rules view."""
        for rule in self._rules:
            rule_path: pathlib.Path = compdef_path.joinpath(
                rule.component.name, rule.name + YAML_EXTENSION
            )
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            self._yaml_transformer.write_to_file(rule, rule_path)

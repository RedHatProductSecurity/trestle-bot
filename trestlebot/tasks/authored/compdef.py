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
import shutil
from typing import List, Optional, Type

import trestle.core.generators as gens
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common.err import TrestleError, TrestleNotFoundError
from trestle.common.list_utils import as_list
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.commands.author.component import ComponentAssemble, ComponentGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


class AuthoredComponentsDefinition(AuthorObjectBase):
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
        try:
            exit_code = ComponentAssemble.assemble_component(
                trestle_root=trestle_root,
                md_name=markdown_path,
                assem_comp_name=compdef,
                parent_comp_name="",
                regenerate=False,
                version=version_tag,
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {compdef}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {compdef}: {e}")

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        """Run assemble actions for compdef type at the provided path"""
        trestle_root = self.get_trestle_root()
        trestle_path = pathlib.Path(trestle_root)
        comp_generate: ComponentGenerate = ComponentGenerate()

        comp_name = os.path.basename(model_path)
        try:
            exit_code = comp_generate.component_generate_all(
                trestle_root=trestle_path,
                comp_def_name=comp_name,
                markdown_dir_name=os.path.join(trestle_root, markdown_path, comp_name),
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
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
        """Create the new component definition with default info"""
        trestle_root: pathlib.Path = pathlib.Path(self.get_trestle_root())

        existing_profile_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, profile_name, prof.Profile
        )

        if existing_profile_path is None:
            raise AuthoredObjectException(
                f"Profile {profile_name} does not exist in the workspace"
            )

        catalog = ProfileResolver.get_resolved_profile_catalog(
            trestle_root,
            existing_profile_path.as_posix(),
        )

        controls = CatalogInterface.get_control_ids_from_catalog(catalog)

        comp_data: Type[comp.ComponentDefinition]
        existing_comp_data_path: Optional[pathlib.Path]

        # Attempt to load the existing compdef if not found create a new instance
        try:
            comp_data, comp_data_path = load_validate_model_name(
                trestle_root,
                compdef_name,
                comp.ComponentDefinition,
                FileContentType.JSON,
            )  # type: ignore
            existing_comp_data_path = pathlib.Path(comp_data_path)
        except TrestleNotFoundError:
            comp_data = gens.generate_sample_model(comp.ComponentDefinition)  # type: ignore
            existing_comp_data_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root,
                compdef_name,
                comp.ComponentDefinition,
                FileContentType.JSON,
            )
            if existing_comp_data_path is None:
                raise AuthoredObjectException(
                    f"Error defining workspace name for component {compdef_name}"
                )

        component = gens.generate_sample_model(comp.DefinedComponent)
        component.type = comp_type
        component.title = comp_title
        component.description = comp_description
        component.control_implementations = []

        get_control_implementation(
            component=component,
            source=existing_profile_path.as_posix(),
            description="",
            controls=controls,
        )

        comp_data.components = as_list(comp_data.components)
        comp_data.components.append(component)

        cd_path = pathlib.Path(existing_comp_data_path)
        if cd_path.parent.exists():
            shutil.rmtree(str(cd_path.parent))

        ModelUtils.update_last_modified(comp_data)  # type: ignore

        cd_path.parent.mkdir(parents=True, exist_ok=True)
        comp_data.oscal_write(path=cd_path)  # type: ignore


def get_control_implementation(
    component: comp.DefinedComponent, source: str, description: str, controls: List[str]
) -> comp.ControlImplementation:
    """Find or create control implementation."""

    component.control_implementations = as_list(component.control_implementations)
    for control_implementation in component.control_implementations:
        if (
            control_implementation.source == source
            and control_implementation.description == description
        ):
            return control_implementation

    control_implementation = gens.generate_sample_model(comp.ControlImplementation)
    control_implementation.source = source
    control_implementation.description = description
    control_implementation.implemented_requirements = []

    for control_id in controls:
        get_implemented_requirement(control_implementation, control_id)

    component.control_implementations.append(control_implementation)
    return control_implementation


def get_implemented_requirement(
    control_implementation: comp.ControlImplementation, control_id: str
) -> comp.ImplementedRequirement:
    """Find or create implemented requirement."""
    for implemented_requirement in control_implementation.implemented_requirements:
        if implemented_requirement.control_id == control_id:
            return implemented_requirement
    implemented_requirement = gens.generate_sample_model(comp.ImplementedRequirement)
    implemented_requirement.control_id = control_id
    control_implementation.implemented_requirements.append(implemented_requirement)
    return implemented_requirement

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

"""Trestle Bot functions for SSP authoring"""

import json
import logging
import os
import pathlib
from typing import Any, Dict, List, Optional

from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPFilter
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.repository import AgileAuthoring
from trestle.oscal.component import ComponentDefinition

from trestlebot.const import COMPDEF_KEY_NAME, LEVERAGED_SSP_KEY_NAME, PROFILE_KEY_NAME
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


logger = logging.getLogger(__name__)


class SSPIndex:
    """
    Class for managing the SSP index that stores relationship data by Trestle name
    for SSPs.
    """

    def __init__(self, index_path: str) -> None:
        """
        Initialize ssp index.
        """
        self._index_path = index_path
        self.profile_by_ssp: Dict[str, str] = {}
        self.comps_by_ssp: Dict[str, List[str]] = {}
        self.leveraged_ssp_by_ssp: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """Load the index from the index file"""
        # Try to load the current file. If it does not exist,
        # create an empty JSON file.
        try:
            with open(self._index_path, "r") as file:
                json_data = json.load(file)

            for ssp_name, ssp_info in json_data.items():
                try:
                    profile = ssp_info[PROFILE_KEY_NAME]
                    component_definitions = ssp_info[COMPDEF_KEY_NAME]
                except KeyError:
                    raise AuthoredObjectException(
                        f"SSP {ssp_name} entry is missing profile or component data"
                    )

                if profile is not None and component_definitions is not None:
                    self.profile_by_ssp[ssp_name] = profile
                    self.comps_by_ssp[ssp_name] = component_definitions

                if LEVERAGED_SSP_KEY_NAME in ssp_info:
                    self.leveraged_ssp_by_ssp[ssp_name] = ssp_info[
                        LEVERAGED_SSP_KEY_NAME
                    ]

        except FileNotFoundError:
            with open(self._index_path, "w") as file:
                json.dump({}, file)

    def reload(self) -> None:
        """Reload the index from the index file"""
        self.profile_by_ssp = {}
        self.comps_by_ssp = {}
        self.leveraged_ssp_by_ssp = {}
        self._load()

    def get_comps_by_ssp(self, ssp_name: str) -> List[str]:
        """Return list of compdefs associated with the SSP"""
        try:
            return self.comps_by_ssp[ssp_name]
        except KeyError:
            raise AuthoredObjectException(
                f"SSP {ssp_name} does not exists in the index"
            )

    def get_profile_by_ssp(self, ssp_name: str) -> str:
        """Return the profile associated with the SSP"""
        try:
            return self.profile_by_ssp[ssp_name]
        except KeyError:
            raise AuthoredObjectException(
                f"SSP {ssp_name} does not exists in the index"
            )

    def get_leveraged_by_ssp(self, ssp_name: str) -> Optional[str]:
        """Return the optional leveraged SSP used with the SSP"""
        try:
            return self.leveraged_ssp_by_ssp[ssp_name]
        except KeyError:
            logging.debug(f"key {ssp_name} does not exist")
            return None

    def add_new_ssp(
        self,
        ssp_name: str,
        profile_name: str,
        compdefs: List[str],
        leveraged_ssp: Optional[str] = None,
    ) -> None:
        """Add a new ssp to the index"""
        self.profile_by_ssp[ssp_name] = profile_name
        self.comps_by_ssp[ssp_name] = compdefs
        if leveraged_ssp:
            self.leveraged_ssp_by_ssp[ssp_name] = leveraged_ssp

    def write_out(self) -> None:
        """Write SSP index back to the index file"""
        data: Dict[str, Any] = {}

        for ssp_name, profile_name in self.profile_by_ssp.items():
            ssp_info: Dict[str, Any] = {
                PROFILE_KEY_NAME: profile_name,
                COMPDEF_KEY_NAME: self.comps_by_ssp[ssp_name],
            }
            if ssp_name in self.leveraged_ssp_by_ssp:
                ssp_info[LEVERAGED_SSP_KEY_NAME] = self.leveraged_ssp_by_ssp[ssp_name]

            data[ssp_name] = ssp_info

        with open(self._index_path, "w") as file:
            json.dump(data, file, indent=4)


class AuthoredSSP(AuthorObjectBase):
    """
    Class for authoring OSCAL SSPs in automation
    """

    def __init__(self, trestle_root: str, ssp_index: SSPIndex) -> None:
        """
        Initialize authored ssps object.
        """
        self.ssp_index = ssp_index
        super().__init__(trestle_root)

    def assemble(self, markdown_path: str, version_tag: str = "") -> None:
        """Run assemble actions for ssp type at the provided path"""
        ssp = os.path.basename(markdown_path)

        comps = self.ssp_index.get_comps_by_ssp(ssp)
        component_str = ",".join(comps)

        trestle_root = pathlib.Path(self.get_trestle_root())
        authoring = AgileAuthoring(trestle_root)

        try:
            success = authoring.assemble_ssp_markdown(
                name=ssp,
                output=ssp,
                markdown_dir=markdown_path,
                regenerate=False,
                version=version_tag,
                compdefs=component_str,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {ssp}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {ssp}: {e}")

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        """Run regenerate actions for ssp type at the provided path"""

        ssp = os.path.basename(model_path)
        comps = self.ssp_index.get_comps_by_ssp(ssp)
        component_str = ",".join(comps)

        profile = self.ssp_index.get_profile_by_ssp(ssp)

        leveraged_ssp = self.ssp_index.get_leveraged_by_ssp(ssp)
        if leveraged_ssp is None:
            leveraged_ssp = ""

        trestle_root = pathlib.Path(self.get_trestle_root())
        authoring = AgileAuthoring(trestle_root)

        try:
            success = authoring.generate_ssp_markdown(
                output=os.path.join(markdown_path, ssp),
                force_overwrite=False,
                yaml_header="",
                overwrite_header_values=False,
                compdefs=component_str,
                profile=profile,
                leveraged_ssp=leveraged_ssp,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while regenerating {ssp}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle generate failed for {ssp}: {e}")

    def create_new_default(
        self,
        ssp_name: str,
        profile_name: str,
        compdefs: List[str],
        markdown_path: str,
        leveraged_ssp: Optional[str] = None,
    ) -> None:
        """
        Create new ssp with index

        Args:
            ssp_name: Output name for ssp
            profile_name: Profile to import controls from
            compdefs: List of component definitions to import
            markdown_path: Top-level markdown path to write to
            leveraged_ssp: Optional leveraged ssp name for inheritance view editing

        Notes:
            This will generate SSP markdown and an index entry for a new managed SSP.
        """

        self.ssp_index.add_new_ssp(ssp_name, profile_name, compdefs, leveraged_ssp)
        self.ssp_index.write_out()

        # Pass the ssp_name as the model base path.
        # We don't need the model dir for SSP generation.
        return self.regenerate(ssp_name, markdown_path)

    def create_new_with_filter(
        self,
        ssp_name: str,
        input_ssp: str,
        version: str = "",
        markdown_path: str = "",
        profile_name: str = "",
        compdefs: Optional[List[str]] = None,
        implementation_status: Optional[List[str]] = None,
        control_origination: Optional[List[str]] = None,
    ) -> None:
        """
        Create new ssp from an ssp with filters.

        Args:
            ssp_name: Output name for ssp
            input_ssp: Input ssp to filter
            profile_name:  Optional profile to filter by
            compdefs: Optional list of component definitions to filter by
            implementation_status: Optional implementation status to filter by
            control_origination: Optional control origination to filter by
            markdown_path: Optional top-level markdown path to write to for continued editing.

        Notes:
            This will transform the SSP with filters. If markdown_path is provided, it will
            also generate SSP markdown and an index entry for a new managed SSP for continued
            management in the workspace.
        """

        # Create new ssp by filtering input ssp
        trestle_root = self.get_trestle_root()
        trestle_path = pathlib.Path(trestle_root)
        ssp_filter: SSPFilter = SSPFilter()

        components_title: Optional[List[str]] = None
        if compdefs:
            components_title = []
            for comp_def_name in compdefs:
                comp_def, _ = ModelUtils.load_model_for_class(
                    trestle_path, comp_def_name, ComponentDefinition
                )
                components_title.extend(
                    [component.title for component in comp_def.components]
                )

        try:
            exit_code = ssp_filter.filter_ssp(
                trestle_root=trestle_path,
                ssp_name=input_ssp,
                profile_name=profile_name,
                out_name=ssp_name,
                regenerate=True,
                components=components_title,
                version=version,
                implementation_status=implementation_status,
                control_origination=control_origination,
            )

            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while filtering {input_ssp}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(
                f"Trestle filtering failed for {input_ssp}: {e}"
            )

        # If markdown_path is provided, create a new managed ssp.
        # this will eventually need to have a JSON to MD recovery to
        # reduce manual editing.
        if markdown_path:
            if not profile_name:
                profile_name = self.ssp_index.get_profile_by_ssp(input_ssp)

            if not compdefs:
                compdefs = self.ssp_index.get_comps_by_ssp(input_ssp)

            leveraged_ssp = self.ssp_index.get_leveraged_by_ssp(input_ssp)

            self.create_new_default(
                ssp_name,
                profile_name,
                compdefs,
                markdown_path,
                leveraged_ssp,
            )

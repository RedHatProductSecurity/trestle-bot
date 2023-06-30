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

import argparse
import json
import logging
import os
import sys
from typing import Dict

from trestle.common.err import TrestleError
from trestle.core.commands.author.ssp import SSPAssemble
from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


logging.basicConfig(
    format="%(levelname)s - %(message)s", stream=sys.stdout, level=logging.INFO
)


class SSPIndex:
    """
    Class for managing the SSP index that stores relationship data by Trestle name
    for SSPs.
    """

    def __init__(self, index_path: str) -> None:
        """
        Initialize ssp index.
        """
        self.profile_by_ssp: Dict[str, str] = {}
        self.comps_by_ssp: Dict[str, str] = {}

        with open(index_path, "r") as file:
            json_data = json.load(file)

        for ssp_name, ssp_info in json_data.items():
            try:
                profile = ssp_info["profile"]
                component_definitions = ssp_info["component_definitions"]
            except KeyError:
                raise AuthoredObjectException(
                    f"SSP {ssp_name} entry has is missing profile or component data"
                )

            if profile is not None and component_definitions is not None:
                component_str = ",".join(component_definitions)
                self.profile_by_ssp[ssp_name] = profile
                self.comps_by_ssp[ssp_name] = component_str

    def get_comps_by_ssp(self, ssp_name: str) -> str:
        """Returns formatted compdef string associated with the SSP"""
        try:
            return self.comps_by_ssp[ssp_name]
        except KeyError:
            raise AuthoredObjectException(
                f"SSP {ssp_name} does not exists in the index"
            )

    def get_profile_by_ssp(self, ssp_name: str) -> str:
        """Returns the profile associated with the SSP"""
        try:
            return self.profile_by_ssp[ssp_name]
        except KeyError:
            raise AuthoredObjectException(
                f"SSP {ssp_name} does not exists in the index"
            )


class AuthoredSSP(AuthorObjectBase):
    """
    Class for authoring OSCAL SSPs in automation
    """

    def __init__(self, trestle_root: str, ssp_index: SSPIndex) -> None:
        """
        Initialize authored ssps object.
        """
        super().__init__(trestle_root)
        self.ssp_index = ssp_index

    def assemble(self, model_path: str, version_tag: str = "") -> None:
        """Run assemble actions for ssp type at the provided path"""
        ssp_assemble: SSPAssemble = SSPAssemble()
        ssp = os.path.basename(model_path)

        comps = self.ssp_index.get_comps_by_ssp(ssp)

        try:
            args = argparse.Namespace(
                trestle_root=self._trestle_root,
                markdown=model_path,
                output=ssp,
                verbose=0,
                regenerate=False,
                version=version_tag,
                name=None,
                compdefs=comps,
            )

            exit_code = ssp_assemble._run(args)
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {ssp}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {ssp}: {e}")

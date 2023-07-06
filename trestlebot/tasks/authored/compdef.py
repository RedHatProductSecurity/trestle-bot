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

from trestle.common.err import TrestleError
from trestle.core.commands.author.component import ComponentAssemble, ComponentGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes

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

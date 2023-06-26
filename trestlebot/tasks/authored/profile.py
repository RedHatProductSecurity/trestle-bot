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

"""Trestle Bot functions for profile authoring"""

import logging
import os
import pathlib
import sys

from trestle.common.err import TrestleError
from trestle.core.commands.author.profile import ProfileAssemble
from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


logging.basicConfig(
    format="%(levelname)s - %(message)s", stream=sys.stdout, level=logging.INFO
)


class AuthoredProfile(AuthorObjectBase):
    """
    Functions for authoring OSCAL Profiles in automation
    """

    def __init__(self, trestle_root: str) -> None:
        """
        Initialize authored profiles object.
        """
        super().__init__(trestle_root)

    def assemble(self, model_path: str, version_tag: str = "") -> None:
        trestle_root = pathlib.Path(self._trestle_root)
        profile = os.path.basename(model_path)
        try:
            exit_code = ProfileAssemble.assemble_profile(
                trestle_root=trestle_root,
                md_name=model_path,
                assem_prof_name=profile,
                parent_prof_name="",
                set_parameters_flag=True,
                regenerate=False,
                version=version_tag,
                allowed_sections=None,
                required_sections=[],
                sections_dict={},
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {profile}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {profile}: {e}")

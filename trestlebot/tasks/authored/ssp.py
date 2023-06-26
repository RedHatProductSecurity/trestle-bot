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


class AuthoredSSP(AuthorObjectBase):
    """
    Functions for authoring OSCAL SSPs in automation
    """

    def __init__(self, trestle_root: str, comps_by_ssp: Dict[str, str]) -> None:
        """
        Initialize authored ssps object.
        """
        super().__init__(trestle_root)
        self.comps_by_ssp = comps_by_ssp

    def assemble(self, model_path: str, version_tag: str = "") -> None:
        ssp_assemble: SSPAssemble = SSPAssemble()
        ssp = os.path.basename(model_path)

        try:
            comps = self.comps_by_ssp[ssp]
        except KeyError:
            raise ValueError(f"{ssp} not in ssp index")

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

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

"""Trestle Bot functions for catalog authoring"""

import os
import pathlib

from trestle.common.err import TrestleError
from trestle.core.repository import AgileAuthoring

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


class AuthoredCatalog(AuthorObjectBase):
    """
    Class for authoring OSCAL catalogs in automation
    """

    def __init__(self, trestle_root: str) -> None:
        """
        Initialize authored catalog.
        """
        super().__init__(trestle_root)

    def assemble(self, markdown_path: str, version_tag: str = "") -> None:
        """Run assemble actions for catalog type at the provided path"""
        trestle_root = pathlib.Path(self.get_trestle_root())
        catalog = os.path.basename(markdown_path)
        authoring = AgileAuthoring(trestle_root)
        try:
            success = authoring.assemble_catalog_markdown(
                name=catalog,
                output=catalog,
                markdown_dir=markdown_path,
                set_parameters=True,
                regenerate=False,
                version=version_tag,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {catalog}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {catalog}: {e}")

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        """Run assemble actions for catalog type at the provided path"""
        trestle_root = pathlib.Path(self.get_trestle_root())
        authoring = AgileAuthoring(trestle_root)

        catalog = os.path.basename(model_path)
        try:
            success = authoring.generate_catalog_markdown(
                name=catalog,
                output=os.path.join(markdown_path, catalog),
                force_overwrite=False,
                yaml_header="",
                overwrite_header_values=False,
            )
            if not success:
                raise AuthoredObjectException(
                    f"Unknown error occurred while regenerating {catalog}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle generate failed for {catalog}: {e}")

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
from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes

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
        trestle_root = pathlib.Path(self.get_trestle_root())
        catalog = os.path.basename(markdown_path)
        try:
            exit_code = CatalogAssemble.assemble_catalog(
                trestle_root=trestle_root,
                md_name=markdown_path,
                assem_cat_name=catalog,
                parent_cat_name="",
                set_parameters_flag=True,
                regenerate=False,
                version=version_tag,
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while assembling {catalog}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle assemble failed for {catalog}: {e}")

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        trestle_root = self.get_trestle_root()
        trestle_path = pathlib.Path(trestle_root)
        catalog_generate: CatalogGenerate = CatalogGenerate()

        catalog = os.path.basename(model_path)
        try:
            exit_code = catalog_generate.generate_markdown(
                trestle_root=trestle_path,
                catalog_path=pathlib.Path(trestle_root, model_path, "catalog.json"),
                markdown_path=pathlib.Path(trestle_root, markdown_path, catalog),
                yaml_header={},
                overwrite_header_values=False,
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while regenerating {catalog}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle generate failed for {catalog}: {e}")

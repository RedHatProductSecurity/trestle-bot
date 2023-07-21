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

import os
import pathlib
import shutil
from typing import Optional, Type

import trestle.core.generators as gens
import trestle.oscal.profile as prof
from trestle.common import const
from trestle.common.err import TrestleError, TrestleNotFoundError
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.profile import ProfileAssemble, ProfileGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.common import IncludeAll

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)


class AuthoredProfile(AuthorObjectBase):
    """
    Class for authoring OSCAL Profiles in automation
    """

    def __init__(self, trestle_root: str) -> None:
        """
        Initialize authored profiles object.
        """
        super().__init__(trestle_root)

    def assemble(self, markdown_path: str, version_tag: str = "") -> None:
        """Run assemble actions for profile type at the provided path"""
        trestle_root = pathlib.Path(self.get_trestle_root())
        profile = os.path.basename(markdown_path)
        try:
            exit_code = ProfileAssemble.assemble_profile(
                trestle_root=trestle_root,
                md_name=markdown_path,
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

    def regenerate(self, model_path: str, markdown_path: str) -> None:
        """Run assemble actions for profile type at the provided path"""
        trestle_root = self.get_trestle_root()
        trestle_path = pathlib.Path(trestle_root)
        profile_generate: ProfileGenerate = ProfileGenerate()

        profile = os.path.basename(model_path)
        try:
            exit_code = profile_generate.generate_markdown(
                trestle_root=trestle_path,
                profile_path=pathlib.Path(trestle_root, model_path, "profile.json"),
                markdown_path=pathlib.Path(trestle_root, markdown_path, profile),
                yaml_header={},
                overwrite_header_values=False,
                sections_dict={},
                required_sections=[],
            )
            if exit_code != CmdReturnCodes.SUCCESS.value:
                raise AuthoredObjectException(
                    f"Unknown error occurred while regenerating {profile}"
                )
        except TrestleError as e:
            raise AuthoredObjectException(f"Trestle generate failed for {profile}: {e}")

    def create_new_default(self, import_path: str, profile_name: str) -> None:
        """
        Create new profile with default info

        Args:
            import_path: Reference to imported catalog or profile (ex. catalogs/example/catalog.json)
            profile_name: Output profile name

        Notes:
            This will attempt to read the output profile at the current name
            and modify it. If one does not exist, a new profile will be created
            with the specified name. The provided import will overwrite the first
            import in the list.

        """
        trestle_root: pathlib.Path = pathlib.Path(self.get_trestle_root())

        profile_data: Type[prof.Profile]
        existing_prof_data_path: Optional[pathlib.Path]

        # Attempt to load the existing profile if not found create a new instance
        try:
            profile_data, prof_data_path = load_validate_model_name(
                trestle_root,
                profile_name,
                prof.Profile,
                FileContentType.JSON,
            )
            existing_prof_data_path = pathlib.Path(prof_data_path)
        except TrestleNotFoundError:
            profile_data = gens.generate_sample_model(prof.Profile)  # type: ignore
            existing_prof_data_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root,
                profile_name,
                prof.Profile,
                FileContentType.JSON,
            )
            if existing_prof_data_path is None:
                raise AuthoredObjectException(
                    f"Error defining workspace name for profile {profile_name}"
                )

        # Update imports
        profile_import: prof.Import = gens.generate_sample_model(prof.Import)
        profile_import.href = const.TRESTLE_HREF_HEADING + import_path
        profile_import.include_all = gens.generate_sample_model(IncludeAll)

        profile_data.imports[0] = profile_import

        # Set up default values for merge settings.
        merge_object: prof.Merge = gens.generate_sample_model(prof.Merge)
        combine_object: prof.Combine = gens.generate_sample_model(prof.Combine)
        combine_object.method = prof.Method.merge
        merge_object.combine = combine_object
        merge_object.as_is = True

        profile_data.merge = merge_object

        profile_path = pathlib.Path(existing_prof_data_path)
        if profile_path.parent.exists():
            shutil.rmtree(str(profile_path.parent))

        ModelUtils.update_last_modified(profile_data)  # type: ignore

        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_data.oscal_write(path=profile_path)  # type: ignore

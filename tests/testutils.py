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

"""Helper functions for unit test setup and teardown."""

import argparse
import json
import pathlib
import shutil
from typing import Dict, List, Optional

from git.repo import Repo
from trestle.common.model_utils import ModelUtils
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog as cat
from trestle.oscal import component as comp
from trestle.oscal import profile as prof

from trestlebot.const import (
    COMPDEF_KEY_NAME,
    LEVERAGED_SSP_KEY_NAME,
    PROFILE_KEY_NAME,
    YAML_EXTENSION,
)


JSON_TEST_DATA_PATH = pathlib.Path("tests/data/json/").resolve()
YAML_TEST_DATA_PATH = pathlib.Path("tests/data/yaml/").resolve()


def clean(repo_path: str, repo: Optional[Repo]) -> None:
    """Clean up the temporary Git repository."""
    if repo is not None:
        repo.close()
    shutil.rmtree(repo_path)


def args_dict_to_list(args_dict: Dict[str, str]) -> List[str]:
    """Transform dictionary of args to a list of args."""
    args = []
    for k, v in args_dict.items():
        args.append(f"--{k}")
        if v is not None:
            args.append(v)
    return args


def load_from_json(
    tmp_trestle_dir: pathlib.Path,
    file_prefix: str,
    model_name: str,
    model_type: OscalBaseModel,
) -> None:
    """Load model from JSON test dir."""
    src_path = JSON_TEST_DATA_PATH / f"{file_prefix}.json"
    dst_path: pathlib.Path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, model_name, model_type, FileContentType.JSON  # type: ignore
    )
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)


def load_from_yaml(
    rules_path: pathlib.Path,
    file_prefix: str,
    dst_name: str = "",
) -> None:
    """Load rule from YAML test dir."""
    if not dst_name:
        dst_name = file_prefix
    src_path = YAML_TEST_DATA_PATH / f"{file_prefix}{YAML_EXTENSION}"
    rules_path = rules_path.joinpath(f"{dst_name}{YAML_EXTENSION}")
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, rules_path)


def setup_for_ssp(
    tmp_trestle_dir: pathlib.Path,
    prof_name: str,
    comps: List[str],
    output_name: str,
) -> argparse.Namespace:
    """Setup trestle temp directory for ssp testing"""
    for comp_name in comps:
        load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)  # type: ignore

    comp_list = ",".join(comps)

    load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)  # type: ignore
    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_catalog",
        "simplified_nist_catalog",
        cat.Catalog,  # type: ignore
    )
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        compdefs=comp_list,
        output=output_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        allowed_sections=None,
        force_overwrite=None,
        leveraged_ssp="",
    )

    return args


def setup_for_profile(
    tmp_trestle_dir: pathlib.Path, prof_name: str, output_name: str
) -> argparse.Namespace:
    """Setup trestle temp directory for profile testing."""
    load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)  # type: ignore

    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_catalog",
        "simplified_nist_catalog",
        cat.Catalog,  # type: ignore
    )

    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=prof_name,
        output=output_name,
        verbose=0,
        yaml_header=None,
        overwrite_header_values=False,
        force_overwrite=None,
        sections=None,
        required_sections=None,
        allowed_sections=None,
    )

    return args


def setup_for_catalog(
    tmp_trestle_dir: pathlib.Path, cat_name: str, output_name: str
) -> argparse.Namespace:
    """Setup trestle temp directory for catalog testing"""
    load_from_json(tmp_trestle_dir, cat_name, cat_name, cat.Catalog)  # type: ignore
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=cat_name,
        output=output_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        force_overwrite=None,
    )

    return args


def setup_for_compdef(
    tmp_trestle_dir: pathlib.Path, comp_name: str, output_name: str
) -> argparse.Namespace:
    """Setup trestle temp directory for component definitions testing"""
    load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)  # type: ignore
    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_profile",
        "simplified_nist_profile",
        prof.Profile,  # type: ignore
    )
    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_catalog",
        "simplified_nist_catalog",
        cat.Catalog,  # type: ignore
    )
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=comp_name,
        output=output_name,
        verbose=0,
        yaml_header=None,
        overwrite_header_values=False,
        force_overwrite=None,
    )

    return args


def setup_rules_view(
    tmp_trestle_dir: pathlib.Path,
    output_name: str,
    rules_dir: str = "rules",
    comp_name: str = "test_comp",
    incomplete_rule: bool = False,
    skip_rules: bool = False,
) -> None:
    """Prepare rules view for testing with a single component definition and test component."""
    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_profile",
        "simplified_nist_profile",
        prof.Profile,  # type: ignore
    )
    load_from_json(
        tmp_trestle_dir,
        "simplified_nist_catalog",
        "simplified_nist_catalog",
        cat.Catalog,  # type: ignore
    )
    rules_path = tmp_trestle_dir.joinpath(rules_dir)
    compdef_dir = rules_path.joinpath(output_name)
    comp_dir = compdef_dir.joinpath(comp_name)
    comp_dir.mkdir(parents=True, exist_ok=True)

    if skip_rules:
        return

    if incomplete_rule:
        load_from_yaml(comp_dir, "test_incomplete_rule")
    else:
        # Load a complete rule with optional fields
        load_from_yaml(comp_dir, "test_complete_rule")
        # Load a complete rule with only required fields
        load_from_yaml(comp_dir, "test_complete_rule_no_params")


def write_index_json(
    file_path: str,
    ssp_name: str,
    profile: str,
    component_definitions: List[str],
    leveraged_ssp: str = "",
) -> None:
    """Write out ssp index JSON for tests"""
    data = {
        ssp_name: {PROFILE_KEY_NAME: profile, COMPDEF_KEY_NAME: component_definitions}
    }

    if leveraged_ssp:
        data[ssp_name][LEVERAGED_SSP_KEY_NAME] = leveraged_ssp

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def replace_string_in_file(file_path: str, old_string: str, new_string: str) -> None:
    """Replace a string in a file."""
    # Read the content of the file
    with open(file_path, "r") as file:
        file_content = file.read()

    # Replace the old string with the new string
    updated_content = file_content.replace(old_string, new_string)

    # Write the updated content back to the file
    with open(file_path, "w") as file:
        file.write(updated_content)

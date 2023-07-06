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
from typing import List, Optional

from git.repo import Repo
from trestle.common.model_utils import ModelUtils
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog as cat
from trestle.oscal import component as comp
from trestle.oscal import profile as prof


JSON_TEST_DATA_PATH = pathlib.Path("tests/data/json/").resolve()


def clean(repo_path: str, repo: Optional[Repo]) -> None:
    # Clean up the temporary Git repository
    if repo is not None:
        repo.close()
    shutil.rmtree(repo_path)


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
    shutil.copy2(src_path, dst_path)  # type: ignore


def setup_for_ssp(
    tmp_trestle_dir: pathlib.Path, prof_name: str, comp_name: str, output_name: str
) -> argparse.Namespace:
    """Setup trestle temp directory for ssp testing"""
    load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)  # type: ignore
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
        compdefs=comp_name,
        output=output_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        allowed_sections=None,
        force_overwrite=None,
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


def write_index_json(
    file_path: str, ssp_name: str, profile: str, component_definitions: List[str]
) -> None:
    """Write out ssp index JSON for tests"""
    data = {
        ssp_name: {"profile": profile, "component_definitions": component_definitions}
    }

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

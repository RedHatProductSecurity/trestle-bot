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

"""Test for Trestle Bot Authored SSP."""

import os
import pathlib

import pytest
from trestle.common import const
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import ssp as ossp

from tests import testutils
from trestlebot.tasks.authored.base_authored import AuthoredObjectException
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_ssp_output = "test-ssp"
markdown_dir = "md_ssp"
leveraged_ssp = "leveraged_ssp"


def test_create_new_with_filter(tmp_trestle_dir: str) -> None:
    """Test to create new SSP with filtering by profile and component definitions"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    authored_ssp.assemble(md_path)

    # Variables for create_new_with_filter
    ssp_name = "new_ssp"
    input_ssp = test_ssp_output
    profile_name = test_prof
    compdefs = [test_comp]

    # Call create_new_with_filter
    authored_ssp.create_new_with_filter(ssp_name, input_ssp, profile_name, compdefs)

    assert ssp_index.get_profile_by_ssp(ssp_name) == profile_name
    _, mpath = load_validate_model_name(
        trestle_root, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON
    )
    assert mpath.exists()


def test_assemble(tmp_trestle_dir: str) -> None:
    """Test to test assemble functionality for SSPs"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    # Run to ensure no exceptions are raised
    authored_ssp.assemble(md_path)

    # Check that the ssp is present in the correct location
    ssp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_ssp_output, ossp.SystemSecurityPlan, FileContentType.JSON
    )
    assert len(ssp.control_implementation.implemented_requirements) == 12


def test_assemble_no_ssp_entry(tmp_trestle_dir: str) -> None:
    """Test to trigger failure for missing SSP index"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, "fake", test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    with pytest.raises(
        AuthoredObjectException, match="SSP test-ssp does not exists in the index"
    ):
        authored_ssp.assemble(md_path)


def test_regenerate(tmp_trestle_dir: str) -> None:
    """Test to test regenerate functionality for SSPs"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(markdown_dir, test_ssp_output)
    _ = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    # Run to ensure no exceptions are raised
    model_path = os.path.join(const.MODEL_DIR_SSP, test_ssp_output)
    authored_ssp.regenerate(model_path, md_path)

    assert os.path.exists(os.path.join(tmp_trestle_dir, markdown_dir, test_ssp_output))


def test_regenerate_no_ssp_entry(tmp_trestle_dir: str) -> None:
    """Test to trigger failure for missing SSP index"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(markdown_dir, test_ssp_output)
    _ = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, "fake", test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    model_path = os.path.join(const.MODEL_DIR_SSP, test_ssp_output)
    with pytest.raises(
        AuthoredObjectException, match="SSP test-ssp does not exists in the index"
    ):
        authored_ssp.regenerate(model_path, md_path)


# SSPIndex tests


def test_get_comps_by_ssp(tmp_trestle_dir: str) -> None:
    """Test to get component definition list from index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(
        ssp_index_path, test_ssp_output, test_prof, [test_comp, "another_comp"]
    )
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    assert test_comp in ssp_index.get_comps_by_ssp(test_ssp_output)
    assert "another_comp" in ssp_index.get_comps_by_ssp(test_ssp_output)


def test_get_profile_by_ssp(tmp_trestle_dir: str) -> None:
    """Test to get profile from index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    assert ssp_index.get_profile_by_ssp(test_ssp_output) == test_prof


def test_get_leveraged_ssp(tmp_trestle_dir: str) -> None:
    """Test to get leveraged ssp from index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(
        ssp_index_path, test_ssp_output, test_prof, [test_comp], leveraged_ssp
    )
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    assert ssp_index.get_leveraged_by_ssp(test_ssp_output) == leveraged_ssp


def test_add_ssp_to_index(tmp_trestle_dir: str) -> None:
    """Test adding an ssp to an index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    ssp_index.add_new_ssp("new_ssp", "test_prof", ["my_comp"])

    assert ssp_index.get_profile_by_ssp("new_ssp") == "test_prof"
    assert "my_comp" in ssp_index.get_comps_by_ssp("new_ssp")
    assert ssp_index.get_leveraged_by_ssp("new_ssp") is None

    ssp_index.add_new_ssp("another_new_ssp", "test_prof", ["my_comp"], "test_leveraged")

    assert ssp_index.get_profile_by_ssp("another_new_ssp") == "test_prof"
    assert "my_comp" in ssp_index.get_comps_by_ssp("another_new_ssp")
    assert ssp_index.get_leveraged_by_ssp("another_new_ssp") == "test_leveraged"

    # Test adding to an empty ssp index

    ssp_index_path = os.path.join(tmp_trestle_dir, "another-ssp-index.json")
    ssp_index = SSPIndex(ssp_index_path)

    ssp_index.add_new_ssp("another_new_ssp", "test_prof", ["my_comp"], "test_leveraged")

    assert ssp_index.get_profile_by_ssp("another_new_ssp") == "test_prof"
    assert "my_comp" in ssp_index.get_comps_by_ssp("another_new_ssp")
    assert ssp_index.get_leveraged_by_ssp("another_new_ssp") == "test_leveraged"


def test_write_new_ssp_index(tmp_trestle_dir: str) -> None:
    """Test writing out a new ssp index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    ssp_index.add_new_ssp("new_ssp", "test_prof", ["my_comp"])
    ssp_index.add_new_ssp("another_new_ssp", "test_prof", ["my_comp"], "test_leveraged")

    ssp_index.write_out()

    # Reread the ssp index from JSON
    ssp_index = SSPIndex(ssp_index_path)

    assert ssp_index.get_profile_by_ssp(test_ssp_output) == test_prof
    assert test_comp in ssp_index.get_comps_by_ssp(test_ssp_output)
    assert ssp_index.get_leveraged_by_ssp(test_ssp_output) is None

    assert ssp_index.get_profile_by_ssp("new_ssp") == "test_prof"
    assert "my_comp" in ssp_index.get_comps_by_ssp("new_ssp")
    assert ssp_index.get_leveraged_by_ssp("new_ssp") is None

    assert ssp_index.get_profile_by_ssp("another_new_ssp") == "test_prof"
    assert "my_comp" in ssp_index.get_comps_by_ssp("another_new_ssp")
    assert ssp_index.get_leveraged_by_ssp("another_new_ssp") == "test_leveraged"

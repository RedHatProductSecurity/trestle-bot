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

import pathlib
from typing import Dict

import pytest
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import ssp as ossp

from tests import testutils
from trestlebot.tasks.authored.ssp import AuthoredSSP


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_ssp_output = "test-ssp"
markdown_dir = "md_ssp"


def test_assemble(tmp_trestle_dir: str) -> None:
    """Test to test assemble functionality for SSPs"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    comps_by_ssp: Dict[str, str] = {}
    comps_by_ssp[test_ssp_output] = test_comp

    authored_ssp = AuthoredSSP(tmp_trestle_dir, comps_by_ssp)

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

    comps_by_ssp: Dict[str, str] = {}
    comps_by_ssp["fake"] = test_comp

    authored_ssp = AuthoredSSP(tmp_trestle_dir, comps_by_ssp)

    with pytest.raises(ValueError):
        authored_ssp.assemble(md_path)

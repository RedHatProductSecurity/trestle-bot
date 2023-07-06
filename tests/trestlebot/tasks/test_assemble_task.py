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

"""Test for Trestle Bot assemble task"""

import os
import pathlib

import pytest
from trestle.core.commands.author.catalog import CatalogGenerate
from trestle.core.commands.author.component import ComponentGenerate
from trestle.core.commands.author.profile import ProfileGenerate
from trestle.core.commands.author.ssp import SSPGenerate

from tests import testutils
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored.types import AuthoredType


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_cat = "simplified_nist_catalog"
test_ssp_output = "my-ssp"

cat_md_dir = "md_cat"
prof_md_dir = "md_prof"
compdef_md_dir = "md_comp"
ssp_md_dir = "md_ssp"


def test_catalog_assemble_task(tmp_trestle_dir: str) -> None:
    """Test catalog assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    args = testutils.setup_for_catalog(trestle_root, test_cat, md_path)
    cat_generate = CatalogGenerate()
    assert cat_generate._run(args) == 0

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.CATALOG.value,
        cat_md_dir,
        "",
    )
    assert assemble_task.execute() == 0


def test_profile_assemble_task(tmp_trestle_dir: str) -> None:
    """Test profile assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(prof_md_dir, test_prof)
    args = testutils.setup_for_profile(trestle_root, test_prof, md_path)
    profile_generate = ProfileGenerate()
    assert profile_generate._run(args) == 0
    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.PROFILE.value,
        prof_md_dir,
        "",
    )
    assert assemble_task.execute() == 0


def test_compdef_assemble_task(tmp_trestle_dir: str) -> None:
    """Test compdef assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(compdef_md_dir, test_comp)
    args = testutils.setup_for_compdef(trestle_root, test_comp, md_path)
    comp_generate = ComponentGenerate()
    assert comp_generate._run(args) == 0
    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.COMPDEF.value,
        compdef_md_dir,
        "",
    )
    assert assemble_task.execute() == 0


def test_ssp_assemble_task(tmp_trestle_dir: str) -> None:
    """Test ssp assemble at the task level"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])

    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.SSP.value,
        ssp_md_dir,
        ssp_index_path,
    )
    assert assemble_task.execute() == 0


def test_ssp_assemble_task_no_index_path(tmp_trestle_dir: str) -> None:
    """Test ssp assemble at the task level with failure"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.SSP.value,
        ssp_md_dir,
        "",
    )
    with pytest.raises(FileNotFoundError):
        assemble_task.execute()

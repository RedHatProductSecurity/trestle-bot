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
from typing import List
from unittest.mock import Mock, patch

import pytest
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.catalog import CatalogGenerate
from trestle.core.commands.author.component import ComponentGenerate
from trestle.core.commands.author.profile import ProfileGenerate
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog as oscal_cat
from trestle.oscal import component as oscal_comp
from trestle.oscal import profile as oscal_prof

from tests import testutils
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored.base_authored import AuthorObjectBase
from trestlebot.tasks.authored.types import AuthoredType


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_cat = "simplified_nist_catalog"
test_ssp_output = "my-ssp"

cat_md_dir = "md_cat"
prof_md_dir = "md_prof"
compdef_md_dir = "md_comp"
ssp_md_dir = "md_ssp"


def test_assemble_task_isolated(tmp_trestle_dir: str) -> None:
    """Test the assemble task isolated from AuthoredObject implementation"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    args = testutils.setup_for_catalog(trestle_root, test_cat, md_path)
    cat_generate = CatalogGenerate()
    assert cat_generate._run(args) == 0

    mock = Mock(spec=AuthorObjectBase)

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.CATALOG.value,
        cat_md_dir,
        "",
    )

    with patch(
        "trestlebot.tasks.authored.types.get_authored_object"
    ) as mock_get_authored_object:
        mock_get_authored_object.return_value = mock

        assert assemble_task.execute() == 0

        mock.assemble.assert_called_once_with(markdown_path=md_path)


@pytest.mark.parametrize(
    "skip_list",
    [
        ["simplified_nist_catalog"],
        ["*nist*"],
        ["simplified_nist_catalog", "simplified_nist_profile"],
        ["*catalog", "*profile"],
    ],
)
def test_assemble_task_with_skip(tmp_trestle_dir: str, skip_list: List[str]) -> None:
    """Test ssp assemble with a skip list"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    args = testutils.setup_for_catalog(trestle_root, test_cat, md_path)
    cat_generate = CatalogGenerate()
    assert cat_generate._run(args) == 0

    mock = Mock(spec=AuthorObjectBase)

    assemble_task = AssembleTask(
        working_dir=tmp_trestle_dir,
        authored_model=AuthoredType.CATALOG.value,
        markdown_dir=cat_md_dir,
        skip_model_list=skip_list,
    )

    with patch(
        "trestlebot.tasks.authored.types.get_authored_object"
    ) as mock_get_authored_object:
        mock_get_authored_object.return_value = mock

        assert assemble_task.execute() == 0
        mock.assemble.assert_not_called()


def test_catalog_assemble_task(tmp_trestle_dir: str) -> None:
    """Test catalog assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    args = testutils.setup_for_catalog(trestle_root, test_cat, md_path)
    cat_generate = CatalogGenerate()
    assert cat_generate._run(args) == 0

    # Get original last modified time
    cat, _ = ModelUtils.load_model_for_class(
        trestle_root, test_cat, oscal_cat.Catalog, FileContentType.JSON
    )
    orig_time = cat.metadata.last_modified

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.CATALOG.value,
        cat_md_dir,
        "",
    )
    assert assemble_task.execute() == 0

    # Get new last modified time and verify catalog was modified
    cat, _ = ModelUtils.load_model_for_class(
        trestle_root, test_cat, oscal_cat.Catalog, FileContentType.JSON
    )
    assert orig_time != cat.metadata.last_modified


def test_profile_assemble_task(tmp_trestle_dir: str) -> None:
    """Test profile assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(prof_md_dir, test_prof)
    args = testutils.setup_for_profile(trestle_root, test_prof, md_path)
    profile_generate = ProfileGenerate()
    assert profile_generate._run(args) == 0

    # Get original last modified time
    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, oscal_prof.Profile, FileContentType.JSON
    )
    orig_time = prof.metadata.last_modified

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.PROFILE.value,
        prof_md_dir,
        "",
    )
    assert assemble_task.execute() == 0

    # Get new last modified time adn verify profile was modified
    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, oscal_prof.Profile, FileContentType.JSON
    )
    assert orig_time != prof.metadata.last_modified


def test_compdef_assemble_task(tmp_trestle_dir: str) -> None:
    """Test compdef assemble at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(compdef_md_dir, test_comp)
    args = testutils.setup_for_compdef(trestle_root, test_comp, md_path)
    comp_generate = ComponentGenerate()
    assert comp_generate._run(args) == 0

    # Get ac-1 markdown file
    comp_path = os.path.join(trestle_root, compdef_md_dir, test_comp, test_comp)
    ac1_md_path = os.path.join(comp_path, test_prof, "ac", "ac-1.md")
    testutils.replace_string_in_file(ac1_md_path, "partial", "implemented")

    # Get original last modified time
    comp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_comp, oscal_comp.ComponentDefinition, FileContentType.JSON
    )
    orig_time = comp.metadata.last_modified

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.COMPDEF.value,
        compdef_md_dir,
        "",
    )
    assert assemble_task.execute() == 0

    # Get new last modified time and verify component was modified
    comp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_comp, oscal_comp.ComponentDefinition, FileContentType.JSON
    )
    assert orig_time != comp.metadata.last_modified


def test_ssp_assemble_task(tmp_trestle_dir: str) -> None:
    """Test ssp assemble at the task level"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])

    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)
    args = testutils.setup_for_ssp(trestle_root, test_prof, [test_comp], md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    assemble_task = AssembleTask(
        tmp_trestle_dir,
        AuthoredType.SSP.value,
        ssp_md_dir,
        ssp_index_path,
    )
    assert assemble_task.execute() == 0

    assert os.path.exists(
        os.path.join(tmp_trestle_dir, "system-security-plans", test_ssp_output)
    )


def test_ssp_assemble_task_no_index_path(tmp_trestle_dir: str) -> None:
    """Test ssp assemble at the task level with failure"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)
    args = testutils.setup_for_ssp(trestle_root, test_prof, [test_comp], md_path)
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

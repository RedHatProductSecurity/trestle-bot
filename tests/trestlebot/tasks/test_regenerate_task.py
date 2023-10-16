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

"""Test for Trestle Bot regenerate task"""

import argparse
import os
import pathlib
from typing import List
from unittest.mock import Mock, patch

import pytest
from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate

from tests import testutils
from trestlebot.tasks.authored.base_authored import AuthorObjectBase
from trestlebot.tasks.authored.types import AuthoredType
from trestlebot.tasks.regenerate_task import RegenerateTask


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_cat = "simplified_nist_catalog"
test_ssp_output = "my-ssp"

cat_md_dir = "md_cat"
prof_md_dir = "md_prof"
compdef_md_dir = "md_comp"
ssp_md_dir = "md_ssp"


def test_regenerate_task_isolated(tmp_trestle_dir: str) -> None:
    """Test the regenerate task isolated from AuthoredObject implementation"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    _ = testutils.setup_for_catalog(trestle_root, test_cat, md_path)

    mock = Mock(spec=AuthorObjectBase)

    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.CATALOG.value,
        cat_md_dir,
        "",
    )

    with patch(
        "trestlebot.tasks.authored.types.get_authored_object"
    ) as mock_get_authored_object:
        mock_get_authored_object.return_value = mock

        assert regenerate_task.execute() == 0

        mock.regenerate.assert_called_once_with(
            model_path=f"catalogs/{test_cat}", markdown_path=cat_md_dir
        )


@pytest.mark.parametrize(
    "skip_list",
    [
        ["simplified_nist_catalog"],
        ["*nist*"],
        ["simplified_nist_catalog", "simplified_nist_profile"],
        ["*catalog", "*profile"],
    ],
)
def test_regenerate_task_with_skip(tmp_trestle_dir: str, skip_list: List[str]) -> None:
    """Test the regenerate task isolated from AuthoredObject implementation"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    _ = testutils.setup_for_catalog(trestle_root, test_cat, md_path)

    mock = Mock(spec=AuthorObjectBase)

    regenerate_task = RegenerateTask(
        working_dir=tmp_trestle_dir,
        authored_model=AuthoredType.CATALOG.value,
        markdown_dir=cat_md_dir,
        skip_model_list=skip_list,
    )

    with patch(
        "trestlebot.tasks.authored.types.get_authored_object"
    ) as mock_get_authored_object:
        mock_get_authored_object.return_value = mock

        assert regenerate_task.execute() == 0

        mock.regenerate.assert_not_called()


def test_catalog_regenerate_task(tmp_trestle_dir: str) -> None:
    """Test catalog regenerate at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    _ = testutils.setup_for_catalog(trestle_root, test_cat, md_path)

    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.CATALOG.value,
        cat_md_dir,
        "",
    )
    assert regenerate_task.execute() == 0
    assert os.path.exists(os.path.join(tmp_trestle_dir, md_path))


def test_catalog_regenerate_task_with_skip(tmp_trestle_dir: str) -> None:
    """Test catalog regenerate at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(cat_md_dir, test_cat)
    _ = testutils.setup_for_catalog(trestle_root, test_cat, md_path)

    regenerate_task = RegenerateTask(
        tmp_trestle_dir, AuthoredType.CATALOG.value, cat_md_dir, "", [test_cat]
    )
    assert regenerate_task.execute() == 0
    assert not os.path.exists(os.path.join(tmp_trestle_dir, md_path))


def test_profile_regenerate_task(tmp_trestle_dir: str) -> None:
    """Test profile regenerate at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(prof_md_dir, test_prof)
    _ = testutils.setup_for_profile(trestle_root, test_prof, md_path)

    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.PROFILE.value,
        prof_md_dir,
        "",
    )
    assert regenerate_task.execute() == 0
    assert os.path.exists(os.path.join(tmp_trestle_dir, md_path))


def test_compdef_regenerate_task(tmp_trestle_dir: str) -> None:
    """Test compdef regenerate at the task level"""
    trestle_root = pathlib.Path(tmp_trestle_dir)

    md_path = os.path.join(compdef_md_dir, test_comp)
    _ = testutils.setup_for_compdef(trestle_root, test_comp, md_path)

    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.COMPDEF.value,
        compdef_md_dir,
        "",
    )
    assert regenerate_task.execute() == 0

    # The compdef is a special case where each component has a separate markdown directory
    assert os.path.exists(os.path.join(tmp_trestle_dir, md_path, test_comp))


def test_ssp_regenerate_task(tmp_trestle_dir: str) -> None:
    """Test ssp regenerate at the task level"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])

    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)

    # Create initial SSP for testing
    args = testutils.setup_for_ssp(trestle_root, test_prof, [test_comp], md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=md_path,
        output=test_ssp_output,
        verbose=0,
        name=None,
        version=None,
        regenerate=False,
        compdefs=args.compdefs,
    )
    assert ssp_assemble._run(args) == 0

    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.SSP.value,
        ssp_md_dir,
        ssp_index_path,
    )
    assert regenerate_task.execute() == 0
    assert os.path.exists(os.path.join(tmp_trestle_dir, md_path))


def test_ssp_regenerate_task_no_index_path(tmp_trestle_dir: str) -> None:
    """Test ssp regenerate at the task level with failure"""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(ssp_md_dir, test_ssp_output)

    # Create initial SSP for testing
    args = testutils.setup_for_ssp(trestle_root, test_prof, [test_comp], md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=md_path,
        output=test_ssp_output,
        verbose=0,
        name=None,
        version=None,
        regenerate=False,
        compdefs=args.compdefs,
    )
    assert ssp_assemble._run(args) == 0
    regenerate_task = RegenerateTask(
        tmp_trestle_dir,
        AuthoredType.SSP.value,
        ssp_md_dir,
        "",
    )

    with pytest.raises(FileNotFoundError):
        regenerate_task.execute()

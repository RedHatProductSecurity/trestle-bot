# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Test for Create SSP CLI"""

import logging
import pathlib
from typing import Any, Dict, Tuple
from unittest.mock import patch

import pytest
from git import Repo

from tests.testutils import TEST_YAML_HEADER, args_dict_to_list, setup_for_ssp
from trestlebot.entrypoints.create_ssp import main as cli_main


@pytest.fixture
def base_args_dict() -> Dict[str, str]:
    return {
        "branch": "main",
        "committer-name": "test",
        "profile-name": "simplified_nist_profile",
        "ssp-name": "test-ssp",
        "committer-email": "test@email.com",
        "working-dir": ".",
        "file-patterns": ".",
    }


test_cat = "simplified_nist_catalog"
test_prof = "simplified_nist_profile"
test_comp_name = "test_comp"
test_ssp_md = "md_ssp"

# Expecting more md files to be included in the commit
# but checking that the md directory was created and the ssp-index.json was created
expected_files = [
    "md_ssp/test-ssp/ac/ac-2.1.md",
    "system-security-plans/test-ssp/system-security-plan.json",
    "index/ssp-index.json",
]


def test_create_ssp(
    tmp_repo: Tuple[str, Repo], base_args_dict: Dict[str, str], caplog: Any
) -> None:
    """Test create-ssp with valid args and a custom yaml header."""
    repo_path, repo = tmp_repo
    tmp_repo_path = pathlib.Path(repo_path)

    args_dict = base_args_dict
    args_dict["working-dir"] = repo_path
    args_dict["markdown-path"] = test_ssp_md
    args_dict["compdefs"] = test_comp_name
    args_dict["ssp-index-path"] = str(tmp_repo_path / "index" / "ssp-index.json")
    args_dict["yaml-header-path"] = str(TEST_YAML_HEADER)

    _ = setup_for_ssp(tmp_repo_path, test_prof, [test_comp_name], test_ssp_md)

    with patch("git.remote.Remote.push") as mock_push, patch(
        "sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]
    ):
        mock_push.return_value = "Mocked Results"
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # Verify that the correct files were included
    commit = next(repo.iter_commits())
    assert all(file in commit.stats.files for file in expected_files)
    assert len(commit.stats.files) == 17

    assert any(
        record.levelno == logging.INFO
        and "Changes pushed to main successfully" in record.message
        for record in caplog.records
    )


def test_create_ssp_with_error(
    tmp_repo: Tuple[str, Repo], base_args_dict: Dict[str, str], caplog: Any
) -> None:
    """Test create-ssp and trigger an error."""
    repo_path, repo = tmp_repo
    tmp_repo_path = pathlib.Path(repo_path)

    args_dict = base_args_dict
    args_dict["working-dir"] = repo_path
    args_dict["markdown-path"] = test_ssp_md
    # Testing with an unloaded compdef
    args_dict["compdefs"] = "fake_comp_name"
    args_dict["ssp-index-path"] = str(tmp_repo_path / "index" / "ssp-index.json")

    _ = setup_for_ssp(tmp_repo_path, test_prof, [test_comp_name], test_ssp_md)

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Component Definition fake_comp_name does not exist in the workspace"
        in record.message
        for record in caplog.records
    )

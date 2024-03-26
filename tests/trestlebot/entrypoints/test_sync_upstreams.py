# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Test for Sync Upstreams CLI"""

import logging
from typing import Any, Dict, Tuple
from unittest.mock import Mock, patch

import pytest
from git import Repo

from tests.testutils import (
    args_dict_to_list,
    clean,
    configure_test_logger,
    prepare_upstream_repo,
)
from trestlebot.entrypoints.sync_upstreams import main as cli_main


@pytest.fixture
def valid_args_dict() -> Dict[str, str]:
    return {
        "branch": "main",
        "sources": "valid_source",
        "committer-name": "test",
        "committer-email": "test@email.com",
        "working-dir": ".",
        "file-patterns": ".",
    }


test_cat = "simplified_nist_catalog"
test_cat_path = "catalogs/simplified_nist_catalog/catalog.json"
test_prof = "simplified_nist_profile"
test_prof_path = "profiles/simplified_nist_profile/profile.json"


def test_sync_upstreams(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with default settings and valid args."""
    repo_path, repo = tmp_repo

    args_dict = valid_args_dict
    args_dict["working-dir"] = repo_path

    source: str = prepare_upstream_repo()

    args_dict["sources"] = f"{source}@main"

    with patch("git.remote.Remote.push") as mock_push, patch(
        "sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]
    ):
        mock_push.return_value = "Mocked Results"
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # Verify that the correct files were included
    commit = next(repo.iter_commits())
    assert test_cat_path in commit.stats.files
    assert test_prof_path in commit.stats.files
    assert len(commit.stats.files) == 2

    # Clean up the source repo
    clean(source, None)


def test_with_include_model_names(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with include model names flag."""
    repo_path, repo = tmp_repo

    args_dict = valid_args_dict
    args_dict["include-model-names"] = test_cat
    args_dict["working-dir"] = repo_path

    source: str = prepare_upstream_repo()

    args_dict["sources"] = f"{source}@main"

    with patch("git.remote.Remote.push") as mock_push, patch(
        "sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]
    ):
        mock_push.return_value = "Mocked Results"
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # Verify that the correct files were included
    commit = next(repo.iter_commits())
    assert test_cat_path in commit.stats.files
    assert len(commit.stats.files) == 1

    # Clean up the source repo
    clean(source, None)


def test_with_exclude_model_names(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with exclude model names flag."""
    repo_path, repo = tmp_repo

    args_dict = valid_args_dict
    args_dict["exclude-model-names"] = test_prof
    args_dict["working-dir"] = repo_path

    source: str = prepare_upstream_repo()
    args_dict["sources"] = f"{source}@main"

    with patch("git.remote.Remote.push") as mock_push, patch(
        "sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]
    ):
        mock_push.return_value = "Mocked Results"
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # Verify that the profile was excluded
    commit = next(repo.iter_commits())
    assert test_cat_path in commit.stats.files
    assert len(commit.stats.files) == 1

    # Clean up the source repo
    clean(source, None)


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_with_no_sources(valid_args_dict: Dict[str, str], caplog: Any) -> None:
    """Test with an invalid source argument."""
    args_dict = valid_args_dict
    args_dict["sources"] = ""

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="2"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Invalid args --sources: Must set at least one source to sync from."
        in record.message
        for record in caplog.records
    )

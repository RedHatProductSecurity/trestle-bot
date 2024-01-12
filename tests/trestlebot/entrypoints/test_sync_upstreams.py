#!/usr/bin/python

#    Copyright 2024 Red Hat, Inc.
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

"""Test for Sync Upstreams CLI"""

import logging
from typing import Any, Dict, Tuple
from unittest.mock import patch

import pytest
from git import Repo

from tests.testutils import args_dict_to_list, clean, prepare_upstream_repo
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
test_repo_url = "git.test.com/test/repo.git"


def test_sync_upstreams(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with default settings and valid args."""
    repo_path, repo = tmp_repo
    repo.create_remote("origin", url=test_repo_url)

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


def test_with_include_models(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with include models flag."""
    repo_path, repo = tmp_repo
    repo.create_remote("origin", url=test_repo_url)

    args_dict = valid_args_dict
    args_dict["include-models"] = test_cat
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


def test_with_exclude_models(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test sync upstreams with exclude models flag."""
    repo_path, repo = tmp_repo
    repo.create_remote("origin", url=test_repo_url)

    args_dict = valid_args_dict
    args_dict["exclude-models"] = test_prof
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

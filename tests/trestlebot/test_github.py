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

"""Test for GitHub provider logic"""

from typing import Tuple

import pytest
from git.repo import Repo

from tests.testutils import clean
from trestlebot.github import GitHub
from trestlebot.provider import GitProviderException


@pytest.mark.parametrize(
    "repo_url",
    [
        "https://github.com/owner/repo",
        "https://github.com/owner/repo.git",
        "github.com/owner/repo.git",
    ],
)
def test_parse_repository(repo_url: str) -> None:
    """Tests parsing valid GitHub repo urls"""
    gh = GitHub("fake")

    owner, repo_name = gh.parse_repository(repo_url)

    assert owner == "owner"
    assert repo_name == "repo"


def test_parse_repository_integration(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests integration with git remote get-url"""
    repo_path, repo = tmp_repo

    repo.create_remote("origin", url="github.com/test/repo.git")

    remote = repo.remote()

    gh = GitHub("fake")

    owner, repo_name = gh.parse_repository(remote.url)

    assert owner == "test"
    assert repo_name == "repo"

    clean(repo_path, repo)


def test_parse_repository_with_incorrect_name() -> None:
    """Test an invalid url input"""
    gh = GitHub("fake")
    with pytest.raises(
        GitProviderException,
        match="https://notgithub.com/owner/repo.git is an invalid GitHub repo URL",
    ):
        gh.parse_repository("https://notgithub.com/owner/repo.git")

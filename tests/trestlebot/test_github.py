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

import json
from typing import Generator, Tuple
from unittest.mock import patch

import pytest
from git.repo import Repo
from responses import GET, POST, RequestsMock

from tests.testutils import JSON_TEST_DATA_PATH, clean
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


@pytest.fixture
def resp_merge_requests() -> Generator[RequestsMock, None, None]:
    """Mock the GitHub API for pull request creation"""
    repo_content = json.load(
        open(JSON_TEST_DATA_PATH / "github_example_repo_response.json")
    )
    pr_content = json.load(
        open(JSON_TEST_DATA_PATH / "github_example_pull_response.json")
    )
    with RequestsMock() as rsps:
        rsps.add(
            method=POST,
            url="https://api.github.com/repos/owner/repo/pulls",
            json=pr_content,
            content_type="application/json",
            status=201,
        )
        rsps.add(
            method=GET,
            url="https://api.github.com/repos/owner/repo",
            json=repo_content,
            content_type="application/json",
            status=200,
        )
        yield rsps


def test_create_pull_request(resp_merge_requests: RequestsMock) -> None:
    """Test creating a pull request"""
    gh = GitHub("fake")
    pr_number = gh.create_pull_request(
        "owner", "repo", "main", "test", "My PR", "Has Changes"
    )
    assert pr_number == 123


def test_create_pull_request_invalid_repo() -> None:
    """Test triggering an error during pull request creation"""
    gh = GitHub("fake")
    with patch("github3.GitHub.repository") as mock_pull:
        mock_pull.return_value = None

        with pytest.raises(
            GitProviderException,
            match="Repository for owner/repo cannot be None",
        ):
            gh.create_pull_request(
                "owner", "repo", "main", "test", "My PR", "Has Changes"
            )
        mock_pull.assert_called_once()

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

"""Test for GitLab provider logic"""

from typing import Callable, Tuple
from unittest.mock import patch

import pytest
from git.repo import Repo
from gitlab.exceptions import GitlabAuthenticationError, GitlabCreateError

from tests.testutils import clean
from trestlebot.gitlab import GitLab
from trestlebot.provider import GitProviderException


@pytest.mark.parametrize(
    "repo_url",
    [
        "https://gitlab.com/owner/repo",
        "https://gitlab.com/owner/repo.git",
        "https://test:test@gitlab.com/owner/repo.git",
        "gitlab.com/owner/repo.git",
    ],
)
def test_parse_repository(repo_url: str) -> None:
    """Tests parsing valid GitLab repo urls"""
    gl = GitLab("fake")

    owner, repo_name = gl.parse_repository(repo_url)

    assert owner == "owner"
    assert repo_name == "repo"


@pytest.mark.parametrize(
    "repo_url",
    [
        "https://mygitlab.com/owner/repo",
        "https://mygitlab.com/owner/repo.git",
        "mygitlab.com/owner/repo.git",
    ],
)
def test_parse_repository_with_server_url(repo_url: str) -> None:
    """Test an invalid url input"""
    gl = GitLab("fake", "https://mygitlab.com")

    owner, repo_name = gl.parse_repository(repo_url)

    assert owner == "owner"
    assert repo_name == "repo"


@pytest.mark.parametrize(
    "repo_url",
    [
        "https://mygitlab.com/group/owner/repo",
        "https://mygitlab.com/group/owner/repo.git",
        "mygitlab.com/group/owner/repo.git",
    ],
)
def test_parse_repository_with_group(repo_url: str) -> None:
    """Test an invalid url input"""
    gl = GitLab("fake", "https://mygitlab.com")

    owner, repo_name = gl.parse_repository(repo_url)

    assert owner == "group/owner"
    assert repo_name == "repo"


def test_parse_repository_integration(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests integration with git remote get-url"""
    repo_path, repo = tmp_repo

    repo.create_remote("origin", url="gitlab.com/test/repo.git")

    remote = repo.remote()

    gl = GitLab("fake")

    owner, repo_name = gl.parse_repository(remote.url)

    assert owner == "test"
    assert repo_name == "repo"

    clean(repo_path, repo)


def test_parse_repository_with_incorrect_name() -> None:
    """Test an invalid url input"""
    gl = GitLab("fake")
    with pytest.raises(
        GitProviderException,
        match="https://notgitlab.com/owner/repo.git is an invalid repo URL",
    ):
        gl.parse_repository("https://notgitlab.com/owner/repo.git")


def create_side_effect(name: str) -> None:
    raise GitlabCreateError("example")


def auth_side_effect(name: str) -> None:
    raise GitlabAuthenticationError("example")


@pytest.mark.parametrize(
    "side_effect, msg",
    [
        (create_side_effect, "Failed to create merge request in .*: example"),
        (
            auth_side_effect,
            "Authentication error during merge request creation in .*: example",
        ),
    ],
)
def test_create_pull_request_with_exceptions(
    side_effect: Callable[[str], None], msg: str
) -> None:
    """Test triggering an error during pull request creation"""
    gl = GitLab("fake")

    with patch("gitlab.v4.objects.ProjectManager.get") as mock_get:
        mock_get.side_effect = side_effect

        with pytest.raises(
            GitProviderException,
            match=msg,
        ):
            gl.create_pull_request(
                "owner", "repo", "main", "test", "My PR", "Has Changes"
            )
        mock_get.assert_called_once()

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

import re
from typing import Callable, Generator, Tuple
from unittest.mock import patch

import pytest
from git.repo import Repo
from gitlab.exceptions import GitlabAuthenticationError, GitlabCreateError
from responses import GET, POST, RequestsMock

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
    """Test with a custom server url"""
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
    """Test with nested namespaces"""
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


mr_content = {
    "id": 123,
    "title": "Example Merge Request",
    "description": "This is an example merge request description.",
    "state": "opened",
    "created_at": "2023-12-06T08:30:00Z",
    "updated_at": "2023-12-06T09:15:00Z",
    "source_branch": "feature-branch",
    "target_branch": "main",
    "author": {"id": 789, "name": "Jane Doe", "username": "janedoe"},
    "merge_status": "can_be_merged",
}


@pytest.fixture
def resp_merge_requests() -> Generator[RequestsMock, None, None]:
    with RequestsMock() as rsps:
        rsps.add(
            method=POST,
            url=re.compile(r"http://localhost/api/v4/projects/1/merge_requests"),
            json=mr_content,
            content_type="application/json",
            status=200,
        )
        rsps.add(
            method=GET,
            url=re.compile(r"http://localhost/api/v4/projects/owner%2Frepo"),
            json={"name": "name", "id": 1},
            content_type="application/json",
            status=200,
        )
        yield rsps


def test_create_pull_request(resp_merge_requests: RequestsMock) -> None:
    """Test creating a pull request"""
    gl = GitLab("fake", "http://localhost")
    pr_number = gl.create_pull_request(
        "owner", "repo", "main", "test", "My PR", "Has Changes"
    )
    assert pr_number == 123


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

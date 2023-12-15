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

"""Test for Entrypoint Base"""

import argparse
from io import StringIO
from typing import Optional
from unittest.mock import patch

import pytest

from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    EntrypointInvalidArgException,
)
from trestlebot.github import GitHub
from trestlebot.gitlab import GitLab
from trestlebot.provider import GitProvider, GitProviderException


@patch.dict("os.environ", {"GITHUB_ACTIONS": "true"})
def test_set_git_provider_with_github() -> None:
    """Test set_git_provider function in Entrypoint Base for GitHub Actions"""
    provider: Optional[GitProvider]
    fake_token = StringIO("fake_token")
    args = argparse.Namespace(target_branch="main", with_token=fake_token)
    provider = EntrypointBase.set_git_provider(args=args)
    assert isinstance(provider, GitHub)


@patch.dict(
    "os.environ",
    {
        "GITHUB_ACTIONS": "false",
        "GITLAB_CI": "true",
        "CI_SERVER_PROTOCOL": "https",
        "CI_SERVER_HOST": "test-gitlab.com",
    },
)
def test_set_git_provider_with_gitlab() -> None:
    """Test set_git_provider function in Entrypoint Base for GitLab CI"""
    provider: Optional[GitProvider]
    fake_token = StringIO("fake_token")
    args = argparse.Namespace(target_branch="main", with_token=fake_token)
    provider = EntrypointBase.set_git_provider(args=args)
    assert isinstance(provider, GitLab)


@patch.dict("os.environ", {"GITHUB_ACTIONS": "false", "GITLAB_CI": "true"})
def test_set_git_provider_with_gitlab_with_failure() -> None:
    """Trigger error with GitLab provider with insufficient environment variables"""
    fake_token = StringIO("fake_token")
    args = argparse.Namespace(target_branch="main", with_token=fake_token)
    with pytest.raises(
        GitProviderException,
        match="Set CI_SERVER_PROTOCOL and CI SERVER HOST environment variables",
    ):
        EntrypointBase.set_git_provider(args=args)


@patch.dict("os.environ", {"GITHUB_ACTIONS": "false"})
def test_set_git_provider_with_none() -> None:
    """Test set_git_provider function when no git provider is set"""
    fake_token = StringIO("fake_token")
    provider: Optional[GitProvider]
    args = argparse.Namespace(target_branch="main", with_token=fake_token)

    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --target-branch: "
        "target-branch flag is set with an unset git provider. To test locally, set the "
        "GITHUB_ACTIONS or GITLAB_CI environment variable.",
    ):
        EntrypointBase.set_git_provider(args=args)

    # Now test with no target branch which is a valid case
    args = argparse.Namespace(target_branch=None, with_token=None)
    provider = EntrypointBase.set_git_provider(args=args)
    assert provider is None


def test_set_provider_with_no_token() -> None:
    """Test set_git_provider function with no token"""
    args = argparse.Namespace(target_branch="main", with_token=None)
    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --with-token: "
        "with-token flag must be set when using target-branch",
    ):
        EntrypointBase.set_git_provider(args=args)

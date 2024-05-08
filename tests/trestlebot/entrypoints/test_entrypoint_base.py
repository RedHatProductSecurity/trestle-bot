# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Test for Entrypoint Base"""

import argparse
from io import StringIO
from typing import Dict, Optional
from unittest.mock import patch

import pytest

from tests.testutils import args_dict_to_list
from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    EntrypointInvalidArgException,
)
from trestlebot.github import GitHub
from trestlebot.gitlab import GitLab
from trestlebot.provider import GitProvider, GitProviderException


@pytest.fixture
def valid_args_dict() -> Dict[str, str]:
    return {
        "branch": "main",
        "committer-name": "test",
        "committer-email": "test@email.com",
        "working-dir": ".",
        "file-patterns": ".",
        "target-branch": "main",
    }


def setup_base_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test parser")
    EntrypointBase(parser=parser)
    return parser.parse_args()


@patch.dict("os.environ", {"GITHUB_ACTIONS": "true"})
def test_base_cli_with_github(valid_args_dict: Dict[str, str]) -> None:
    """Test set_git_provider function in Entrypoint Base for GitHub Actions"""
    provider: Optional[GitProvider]
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(valid_args_dict)]):
        args = setup_base_cli()
        vars(args)["with_token"] = StringIO("fake_token")
        provider = EntrypointBase.set_git_provider(args=args)
        assert isinstance(provider, GitHub)


@patch.dict(
    "os.environ",
    {"GITHUB_ACTIONS": "true", "TRESTLEBOT_REPO_ACCESS_TOKEN": "fake_token"},
)
def test_base_cli_with_github_no_stdin(valid_args_dict: Dict[str, str]) -> None:
    """Test set_git_provider function in Entrypoint Base for GitHub Actions"""
    provider: Optional[GitProvider]
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(valid_args_dict)]):
        args = setup_base_cli()
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
def test_base_cli_with_gitlab(valid_args_dict: Dict[str, str]) -> None:
    """Test set_git_provider function in Entrypoint Base for GitLab CI"""
    provider: Optional[GitProvider]
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(valid_args_dict)]):
        args = setup_base_cli()
        vars(args)["with_token"] = StringIO("fake_token")
        provider = EntrypointBase.set_git_provider(args=args)
        assert isinstance(provider, GitLab)


@patch.dict("os.environ", {"GITHUB_ACTIONS": "false", "GITLAB_CI": "true"})
def test_base_cli_with_gitlab_with_failure(valid_args_dict: Dict[str, str]) -> None:
    """Trigger error with GitLab provider with insufficient environment variables"""
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(valid_args_dict)]):
        with pytest.raises(
            GitProviderException,
            match="Set CI_SERVER_PROTOCOL and CI SERVER HOST environment variables",
        ):
            setup_base_cli()


@patch.dict("os.environ", {"GITHUB_ACTIONS": "false", "GITLAB_CI": "false"})
def test_base_cli_with_provide_type_set(valid_args_dict: Dict[str, str]) -> None:
    """Trigger error with GitLab provider with insufficient environment variables"""
    args_dict = valid_args_dict
    args_dict["git-provider-type"] = "gitlab"
    args_dict["git-server-url"] = "https://mygitlab.com"
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(valid_args_dict)]):
        args = setup_base_cli()
        vars(args)["with_token"] = StringIO("fake_token")
        provider = EntrypointBase.set_git_provider(args=args)
        assert isinstance(provider, GitLab)


@patch.dict("os.environ", {"GITHUB_ACTIONS": "false"})
def test_set_git_provider_with_none() -> None:
    """Test set_git_provider function when no git provider is set"""
    provider: Optional[GitProvider]
    args = argparse.Namespace(
        target_branch="main",
        with_token=StringIO("fake_token"),
        git_provider_type="",
        git_server_url="",
    )

    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --target-branch, --git-provider-type: "
        "Could not determine Git provider from inputs",
    ):
        EntrypointBase.set_git_provider(args=args)

    # Now test with no target branch which is a valid case
    args = argparse.Namespace(target_branch=None)
    provider = EntrypointBase.set_git_provider(args=args)
    assert provider is None

    args = argparse.Namespace(target_branch="")
    provider = EntrypointBase.set_git_provider(args=args)
    assert provider is None


def test_set_provider_with_no_token() -> None:
    """Test set_git_provider function with no token"""
    args = argparse.Namespace(target_branch="main", with_token=None)
    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --with-token: with-token flag must be set to read from standard input "
        "or use TRESTLEBOT_REPO_ACCESS_TOKEN environment variable when using target-branch",
    ):
        EntrypointBase.set_git_provider(args=args)


def test_set_provider_with_input() -> None:
    """Test set_git_provider function with type and server url input."""
    provider: Optional[GitProvider]
    args = argparse.Namespace(
        target_branch="main",
        with_token=StringIO("fake_token"),
        git_provider_type="github",
        git_server_url="",
    )
    provider = EntrypointBase.set_git_provider(args=args)
    assert isinstance(provider, GitHub)
    args = argparse.Namespace(
        target_branch="main",
        with_token=StringIO("fake_token"),
        git_provider_type="gitlab",
        git_server_url="",
    )
    provider = EntrypointBase.set_git_provider(args=args)
    assert isinstance(provider, GitLab)

    args = argparse.Namespace(
        target_branch="main",
        with_token=StringIO("fake_token"),
        git_provider_type="github",
        git_server_url="https://notgithub.com",
    )
    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --git-server-url: GitHub provider does not support custom server URLs",
    ):
        EntrypointBase.set_git_provider(args=args)

    args = argparse.Namespace(
        target_branch="main",
        with_token=StringIO("fake_token"),
        git_provider_type="",
        git_server_url="https://github.com",
    )
    with pytest.raises(
        EntrypointInvalidArgException,
        match="Invalid args --git-provider-type: git-provider-type must be set when using "
        "git-server-url",
    ):
        EntrypointBase.set_git_provider(args=args)

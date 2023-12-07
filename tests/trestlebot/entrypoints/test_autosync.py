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

"""Test for Autosync CLI"""

import logging
from typing import Any, Dict
from unittest.mock import patch

import pytest

from tests.testutils import args_dict_to_list
from trestlebot.entrypoints.autosync import main as cli_main


@pytest.fixture
def valid_args_dict() -> Dict[str, str]:
    return {
        "branch": "main",
        "markdown-path": "/my/path",
        "oscal-model": "profile",
        "committer-name": "test",
        "committer-email": "test@email.com",
        "working-dir": ".",
        "file-patterns": ".",
    }


def test_invalid_oscal_model(valid_args_dict: Dict[str, str]) -> None:
    """Test invalid oscal model"""
    args_dict = valid_args_dict
    args_dict["oscal-model"] = "fake"
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="2"):
            cli_main()


def test_no_ssp_index(valid_args_dict: Dict[str, str], caplog: Any) -> None:
    """Test missing index file for ssp"""
    args_dict = valid_args_dict
    args_dict["oscal-model"] = "ssp"
    args_dict["ssp-index-path"] = ""
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="2"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Invalid args --ssp-index-path: Must set ssp index path when using SSP as "
        "oscal model." in record.message
        for record in caplog.records
    )


def test_no_markdown_path(valid_args_dict: Dict[str, str], caplog: Any) -> None:
    """Test without a markdown file passed as a flag"""
    args_dict = valid_args_dict
    args_dict["markdown-path"] = ""
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="2"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Invalid args --markdown-path: Markdown path must be set." in record.message
        for record in caplog.records
    )


def test_non_existent_working_dir(valid_args_dict: Dict[str, str], caplog: Any) -> None:
    """Test with a non-existent working directory"""
    args_dict = valid_args_dict
    args_dict["working-dir"] = "tmp"
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Root path tmp does not exist" in record.message
        for record in caplog.records
    )


def test_with_target_branch(valid_args_dict: Dict[str, str], caplog: Any) -> None:
    """Test with target branch set an an unsupported Git provider"""
    args_dict = valid_args_dict
    args_dict["target-branch"] = "main"

    # Patch is_github_actions since these tests will be running in
    # GitHub Actions
    with patch(
        "trestlebot.entrypoints.entrypoint_base.is_github_actions"
    ) as mock_check, patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        mock_check.return_value = False

        with pytest.raises(SystemExit, match="2"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Invalid args --target-branch: target-branch flag is set with an "
        "unset git provider. To test locally, set the GITHUB_ACTIONS or GITLAB_CI environment variable."
        in record.message
        for record in caplog.records
    )

    mock_check.assert_called_once()

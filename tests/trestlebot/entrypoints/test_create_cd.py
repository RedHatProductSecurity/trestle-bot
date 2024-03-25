# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Test for Create CD CLI"""

import logging
import pathlib
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from tests.testutils import args_dict_to_list, setup_for_compdef
from trestlebot.entrypoints.create_cd import main as cli_main
from trestlebot.entrypoints.log import configure_test_logger


@pytest.fixture
def valid_args_dict() -> Dict[str, str]:
    return {
        "profile-name": "simplified_nist_profile",
        "component-title": "test-comp",
        "compdef-name": "test-compdef",
        "component-description": "test",
        "markdown-path": "markdown",
        "branch": "test",
        "committer-name": "test",
        "committer-email": "test@email.com",
    }


test_comp_name = "test_comp"
test_ssp_cd = "md_cd"


def test_create_cd_with_missing_args(
    tmp_trestle_dir: str, valid_args_dict: Dict[str, str]
) -> None:
    """Test create cd and trigger error."""
    tmp_repo_path = pathlib.Path(tmp_trestle_dir)

    args_dict = valid_args_dict
    del args_dict["profile-name"]

    _ = setup_for_compdef(tmp_repo_path, test_comp_name, test_ssp_cd)

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="2"):
            cli_main()


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_create_cd_with_missing_profile(
    tmp_trestle_dir: str, valid_args_dict: Dict[str, str], caplog: Any
) -> None:
    """Test create cd and trigger error."""
    tmp_repo_path = pathlib.Path(tmp_trestle_dir)

    args_dict = valid_args_dict
    args_dict["profile-name"] = "invalid_prof"
    args_dict["working-dir"] = tmp_trestle_dir

    _ = setup_for_compdef(tmp_repo_path, test_comp_name, test_ssp_cd)

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Profile invalid_prof does not exist in the workspace" in record.message
        for record in caplog.records
    )


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_create_cd_with_missing_filter_profile(
    tmp_trestle_dir: str, valid_args_dict: Dict[str, str], caplog: Any
) -> None:
    """Test create cd and trigger error."""
    tmp_repo_path = pathlib.Path(tmp_trestle_dir)

    args_dict = valid_args_dict
    args_dict["filter-by-profile"] = "invalid_prof"
    args_dict["working-dir"] = tmp_trestle_dir

    _ = setup_for_compdef(tmp_repo_path, test_comp_name, test_ssp_cd)

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and "Profile invalid_prof does not exist in the workspace" in record.message
        for record in caplog.records
    )

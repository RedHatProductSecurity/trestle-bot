# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Test for Rules Transform CLI"""

import pathlib
from typing import Dict, Tuple
from unittest.mock import patch

import pytest
from git import Repo

from tests.testutils import args_dict_to_list, setup_for_compdef, setup_rules_view
from trestlebot.entrypoints.rule_transform import main as cli_main


@pytest.fixture
def valid_args_dict() -> Dict[str, str]:
    return {
        "markdown-path": "markdown",
        "branch": "test",
        "committer-name": "test",
        "committer-email": "test@email.com",
    }


test_comp_name = "test_comp"
test_md = "md_cd"


def test_rules_transform(
    tmp_repo: Tuple[str, Repo], valid_args_dict: Dict[str, str]
) -> None:
    """Test rules transform on a happy path."""
    repo_path, _ = tmp_repo

    args_dict = valid_args_dict
    args_dict["working-dir"] = repo_path

    _ = setup_for_compdef(pathlib.Path(repo_path), test_comp_name, test_md)
    setup_rules_view(pathlib.Path(repo_path), test_comp_name)

    with patch("sys.argv", ["trestlebot", "--dry-run", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="0"):
            cli_main()

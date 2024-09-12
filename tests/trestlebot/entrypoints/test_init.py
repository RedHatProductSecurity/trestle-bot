# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Test for Init CLI entrypoint"""
import argparse
import logging
import pathlib
from typing import Dict
from unittest.mock import Mock, patch

import pytest
from trestle.common.const import TRESTLE_CONFIG_DIR, TRESTLE_KEEP_FILE
from trestle.common.file_utils import is_hidden

from tests.testutils import args_dict_to_list, configure_test_logger, setup_for_init
from trestlebot.const import TRESTLEBOT_CONFIG_DIR
from trestlebot.entrypoints.init import InitEntrypoint
from trestlebot.entrypoints.init import main as cli_main
from trestlebot.tasks.authored import types as model_types


OSCAL_MODEL_SSP = model_types.AuthoredType.SSP.value
OSCAL_MODEL_COMPDEF = model_types.AuthoredType.COMPDEF.value


@pytest.fixture
def args_dict() -> Dict[str, str]:
    return {
        "working-dir": ".",
        "oscal-model": OSCAL_MODEL_COMPDEF,
    }


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_init_fails_if_trestlebot_dir_exists(
    tmp_init_dir: str, args_dict: Dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """Trestlebot init should fail if .trestlebot directory already exists"""
    setup_for_init(pathlib.Path(tmp_init_dir))

    args_dict["working-dir"] = tmp_init_dir

    # Manulaly create .trestlebot dir so it already exists
    trestlebot_dir = pathlib.Path(tmp_init_dir) / pathlib.Path(TRESTLEBOT_CONFIG_DIR)
    trestlebot_dir.mkdir()

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and f"Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in"
        in record.message
        for record in caplog.records
    )


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_init_if_not_git_repo(
    tmp_init_dir: str, args_dict: Dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """Test init fails if not in git repo directory"""
    args_dict["working-dir"] = tmp_init_dir
    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    assert any(
        record.levelno == logging.ERROR
        and f"Initialization failed. Given directory {tmp_init_dir} is not a Git repository."
        in record.message
        for record in caplog.records
    )


def test_call_trestle_init(tmp_init_dir: str) -> None:
    """Tests for expected results of calling trestle init"""
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(verbose=0, working_dir=tmp_init_dir)
    InitEntrypoint(parser=parser)._call_trestle_init(args)
    tmp_dir = pathlib.Path(tmp_init_dir)
    trestle_dir = tmp_dir / pathlib.Path(TRESTLE_CONFIG_DIR)
    keep_file = trestle_dir / pathlib.Path(TRESTLE_KEEP_FILE)
    assert keep_file.exists() is True


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_init_compdef(
    tmp_init_dir: str, args_dict: Dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """Tests for expected init command directories and files"""
    args_dict["working-dir"] = tmp_init_dir
    args_dict["oscal-model"] = model_types.AuthoredType.COMPDEF.value

    setup_for_init(pathlib.Path(tmp_init_dir))

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # directories for compdef model should exist
    tmp_dir = pathlib.Path(tmp_init_dir)
    model_dirs = [d.name for d in tmp_dir.iterdir() if not is_hidden(d)]
    expected = InitEntrypoint.MODEL_DIRS[args_dict["oscal-model"]] + [
        InitEntrypoint.MARKDOWN_DIR
    ]
    assert sorted(model_dirs) == sorted(expected)

    # markdown directories should exist
    markdown_dir = tmp_dir.joinpath(InitEntrypoint.MARKDOWN_DIR)
    expected_subdirs = InitEntrypoint.MODEL_DIRS[args_dict["oscal-model"]]
    markdown_subdirs = [f.name for f in markdown_dir.iterdir()]
    assert sorted(markdown_subdirs) == sorted(expected_subdirs)

    assert any(
        record.levelno == logging.INFO
        and f"Initialized trestlebot project successfully in {tmp_init_dir}"
        in record.message
        for record in caplog.records
    )


@patch(
    "trestlebot.entrypoints.log.configure_logger",
    Mock(side_effect=configure_test_logger),
)
def test_init_ssp(
    tmp_init_dir: str, args_dict: Dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """Tests for expected init command directories and files"""
    args_dict["working-dir"] = tmp_init_dir
    args_dict["oscal-model"] = model_types.AuthoredType.SSP.value

    setup_for_init(pathlib.Path(tmp_init_dir))

    with patch("sys.argv", ["trestlebot", *args_dict_to_list(args_dict)]):
        with pytest.raises(SystemExit, match="0"):
            cli_main()

    # directories for compdef model should exist
    tmp_dir = pathlib.Path(tmp_init_dir)
    model_dirs = [d.name for d in tmp_dir.iterdir() if not is_hidden(d)]
    expected = InitEntrypoint.MODEL_DIRS[args_dict["oscal-model"]] + [
        InitEntrypoint.MARKDOWN_DIR
    ]
    assert sorted(model_dirs) == sorted(expected)

    # markdown directories should exist
    markdown_dir = tmp_dir.joinpath(InitEntrypoint.MARKDOWN_DIR)
    expected_subdirs = InitEntrypoint.MODEL_DIRS[args_dict["oscal-model"]]
    markdown_subdirs = [f.name for f in markdown_dir.iterdir()]
    assert sorted(markdown_subdirs) == sorted(expected_subdirs)

    assert any(
        record.levelno == logging.INFO
        and f"Initialized trestlebot project successfully in {tmp_init_dir}"
        in record.message
        for record in caplog.records
    )

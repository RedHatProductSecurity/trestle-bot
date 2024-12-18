# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Testing module for trestlebot init command"""
import pathlib

import yaml
from click.testing import CliRunner
from trestle.common.const import MODEL_DIR_LIST, TRESTLE_CONFIG_DIR, TRESTLE_KEEP_FILE
from trestle.common.file_utils import is_hidden

from tests.testutils import setup_for_init
from trestlebot.cli.commands.init import call_trestle_init, init_cmd
from trestlebot.const import TRESTLEBOT_CONFIG_DIR


def test_init_repo_dir_does_not_exist() -> None:
    """Init should fail if repo dir does not exit"""
    runner = CliRunner()
    result = runner.invoke(init_cmd, ["--repo-path", "0"])
    assert result.exit_code == 2
    assert "does not exist." in result.output


def test_init_not_git_repo(tmp_init_dir: str) -> None:
    """Init should fail if repo dir is not a Git repo."""
    runner = CliRunner()
    result = runner.invoke(
        init_cmd, ["--repo-path", tmp_init_dir, "--markdown-dir", "markdown"]
    )
    assert result.exit_code == 1
    assert "not a Git repository" in result.output


def test_init_existing_trestlebot_dir(tmp_init_dir: str) -> None:
    """Init should fail if repo already contains .trestlebot/ dir."""

    # setup_for_init(pathlib.Path(tmp_init_dir))
    # Manulaly create .trestlebot dir so it already exists
    trestlebot_dir = pathlib.Path(tmp_init_dir) / pathlib.Path(TRESTLEBOT_CONFIG_DIR)
    trestlebot_dir.mkdir()

    setup_for_init(pathlib.Path(tmp_init_dir))

    runner = CliRunner()
    result = runner.invoke(
        init_cmd, ["--repo-path", tmp_init_dir, "--markdown-dir", "markdown"]
    )

    assert result.exit_code == 1
    assert "existing .trestlebot directory" in result.output


def test_init_creates_config_file(tmp_init_dir: str) -> None:
    """Test init command creates yaml config file."""

    setup_for_init(pathlib.Path(tmp_init_dir))

    runner = CliRunner()
    result = runner.invoke(
        init_cmd, ["--repo-path", tmp_init_dir, "--markdown-dir", "markdown"]
    )
    assert result.exit_code == 0
    assert "Successfully initialized trestlebot" in result.output

    config_path = (
        pathlib.Path(tmp_init_dir)
        .joinpath(TRESTLEBOT_CONFIG_DIR)
        .joinpath("config.yml")
    )
    with open(config_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    assert yaml_data["repo_path"] == tmp_init_dir
    assert yaml_data["markdown_dir"] == "markdown"


def test_init_creates_model_dirs(tmp_init_dir: str) -> None:
    """Init should create model directories in repo"""

    tmp_dir = pathlib.Path(tmp_init_dir)
    setup_for_init(tmp_dir)

    runner = CliRunner()
    runner.invoke(init_cmd, ["--repo-path", tmp_init_dir, "--markdown-dir", "markdown"])

    model_dirs = [d.name for d in tmp_dir.iterdir() if not is_hidden(d)]
    model_dirs.remove("markdown")  # pop markdown dir
    assert sorted(model_dirs) == sorted(MODEL_DIR_LIST)


def test_init_creates_markdown_dirs(tmp_init_dir: str) -> None:
    """Init should create model directories in repo"""

    tmp_dir = pathlib.Path(tmp_init_dir)
    markdown_dir = tmp_dir.joinpath("markdown")
    setup_for_init(tmp_dir)

    runner = CliRunner()
    runner.invoke(init_cmd, ["--repo-path", tmp_init_dir, "--markdown-dir", "markdown"])

    markdown_dirs = [d.name for d in markdown_dir.iterdir() if not is_hidden(d)]
    assert sorted(markdown_dirs) == sorted(MODEL_DIR_LIST)


def test_init_creates_trestle_dirs(tmp_init_dir: str) -> None:
    """Init should create markdown dirs in repo"""

    tmp_dir = pathlib.Path(tmp_init_dir)
    call_trestle_init(tmp_dir, False)
    trestle_dir = tmp_dir.joinpath(TRESTLE_CONFIG_DIR)
    keep_file = trestle_dir.joinpath(TRESTLE_KEEP_FILE)
    assert keep_file.exists() is True

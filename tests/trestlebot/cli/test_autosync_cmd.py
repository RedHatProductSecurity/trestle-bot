# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Testing module for trestlebot autosync command"""
import pathlib
from typing import Tuple

from click.testing import CliRunner
from git import Repo

from trestlebot.cli.commands.autosync import autosync_cmd
from trestlebot.cli.config import TrestleBotConfig, write_to_file


def test_invalid_oscal_model(tmp_init_dir: str) -> None:
    """Test invalid OSCAl model option"""
    runner = CliRunner()
    result = runner.invoke(
        autosync_cmd,
        [
            "--oscal-model",
            "invalid",
            "--repo-path",
            tmp_init_dir,
            "--markdown-dir",
            "markdown",
            "--branch",
            "main",
            "--committer-name",
            "Test User",
            "--committer-email",
            "test@example.com",
        ],
    )
    assert "Invalid value for '--oscal-model'" in result.output
    assert result.exit_code == 2


def test_missing_ssp_index_path(tmp_init_dir: str) -> None:
    """Test missing ssp-index-file for autosync ssp."""

    runner = CliRunner()
    cmd_options = [
        "--oscal-model",
        "ssp",
        "--repo-path",
        tmp_init_dir,
        "--markdown-dir",
        "markdown",
        "--branch",
        "main",
        "--committer-name",
        "Test User",
        "--committer-email",
        "test@example.com",
    ]
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 1
    assert "Missing option '--ssp-index-file'" in result.output


def test_missing_markdown_dir(tmp_repo: Tuple[str, Repo]) -> None:

    repo_path, _ = tmp_repo
    runner = CliRunner()
    cmd_options = [
        "--oscal-model",
        "compdef",
        "--repo-path",
        repo_path,
        "--branch",
        "main",
        "--committer-name",
        "Test User",
        "--committer-email",
        "test@example.com",
    ]
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 2
    assert "Error: Missing option '--markdown-dir'" in result.output

    # With 'markdown_dir' setting in config.yml
    config_obj = TrestleBotConfig(markdown_dir="markdown")
    filepath = pathlib.Path(repo_path).joinpath("config.yml")
    write_to_file(config_obj, filepath)
    cmd_options += ["--config", str(filepath)]
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 0

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Testing module for trestlebot autosync command"""
import pathlib
from typing import Tuple

from click.testing import CliRunner
from git import Repo

from trestlebot.cli.commands.autosync import autosync_cmd
from trestlebot.cli.config import TrestleBotConfig, write_to_file


def test_invalid_autosync_command(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, _ = tmp_repo
    runner = CliRunner()
    result = runner.invoke(
        autosync_cmd,
        [
            "invalid",
            "--repo-path",
            repo_path,
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
    assert "Error: No such command" in result.output
    assert result.exit_code == 2


def test_no_ssp_index_path(tmp_repo: Tuple[str, Repo]) -> None:
    """Test ssp_index_file for autosync ssp"""
    repo_path, _ = tmp_repo
    runner = CliRunner()
    cmd_options = [
        "ssp",
        "--repo-path",
        repo_path,
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
    assert result.exit_code == 2
    assert "Error: Missing option '--ssp-index-file'" in result.output
    cmd_options[0] = "compdef"
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 0


def test_no_markdown_dir(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, _ = tmp_repo
    runner = CliRunner()
    cmd_options = [
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

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Testing module for trestlebot autosync command"""
import tempfile

from click.testing import CliRunner

from trestlebot.cli.commands.autosync import autosync_cmd


def test_invalid_autosync_command(tmp_init_dir: str) -> None:
    tempdir = tempfile.mkdtemp()
    runner = CliRunner()
    result = runner.invoke(
        autosync_cmd,
        [
            "invalid",
            "--repo-path",
            tmp_init_dir,
            "--markdown-path",
            tempdir,
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


def test_no_ssp_index_path(tmp_init_dir: str) -> None:
    """Test invalid ssp index file for autosync ssp"""

    tempdir = tempfile.mkdtemp()
    runner = CliRunner()
    cmd_options = [
        "ssp",
        "--repo-path",
        tmp_init_dir,
        "--markdown-path",
        tempdir,
        "--branch",
        "main",
        "--committer-name",
        "Test User",
        "--committer-email",
        "test@example.com",
    ]
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 2
    assert "Error: Missing option '--ssp-index-path'" in result.output
    cmd_options[0] = "compdef"
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 0


def test_no_markdown_path(tmp_init_dir: str) -> None:
    runner = CliRunner()
    cmd_options = [
        "compdef",
        "--repo-path",
        tmp_init_dir,
        "--branch",
        "main",
        "--committer-name",
        "Test User",
        "--committer-email",
        "test@example.com",
    ]
    result = runner.invoke(autosync_cmd, cmd_options)
    assert result.exit_code == 2
    assert "Error: Missing option '--markdown-path'" in result.output

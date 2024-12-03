# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Testing module for trestlebot autosync command"""
import tempfile

from click.testing import CliRunner

from trestlebot.cli.commands.autosync import autosync_cmd


def test_invalid_oscal_model(tmp_init_dir: str) -> None:
    """Test invalid OSCAl model option"""
    tempdir = tempfile.mkdtemp()
    runner = CliRunner()
    result = runner.invoke(
        autosync_cmd,
        [
            "--oscal-model",
            "invalid",
            "--repo-path",
            tmp_init_dir,
            "--markdown-dir",
            tempdir,
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


def test_no_ssp_index_path(tmp_init_dir: str) -> None:
    """Test missing ssp-index-file for autosync ssp."""

    tempdir = tempfile.mkdtemp()
    runner = CliRunner()
    cmd_options = [
        "--oscal-model",
        "ssp",
        "--repo-path",
        tmp_init_dir,
        "--markdown-dir",
        tempdir,
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


def test_missing_markdown_dir_option(tmp_init_dir: str) -> None:
    """Test autosync required markdown-dir option."""

    runner = CliRunner()
    cmd_options = [
        "--oscal-model",
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
    assert "Error: Missing option '--markdown-dir'" in result.output

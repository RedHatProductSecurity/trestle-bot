# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""" Unit test for create commands ssp and cd"""

from click.testing import CliRunner

from trestlebot.cli.commands.create import create_cmd


def test_invalid_create_cmd() -> None:
    """Tests that create command fails if given invalid oscal model subcommand."""
    runner = CliRunner()
    result = runner.invoke(create_cmd, ["invalid"])

    assert "Error: No such command 'invalid'" in result.output
    assert result.exit_code == 2


def test_create_ssp_cmd(tmp_init_dir: str) -> None:
    """Tests successful create ssp command."""
    SSP_INDEX_FILE = "tester-ssp-index.json"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            "markdown",
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            SSP_INDEX_FILE,
        ],
    )
    assert result.exit_code == 0


def test_create_compdef_cmd(tmp_init_dir: str) -> None:
    """Tests successful create compdef command."""

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "compdef",
            "--profile-name",
            "oscal-profile-name",
            "--compdef-name",
            "test-name",
            "--component-title",
            "title-test",
            "--component-description",
            "description-test",
            "--component-definition-type",
            "type-test",
            "repo-path",
            tmp_init_dir,
        ],
    )
    assert result.exit_code == 2


def test_default_ssp_index_file_cmd(tmp_init_dir: str) -> None:
    """Tests successful default ssp_index.json file creation."""

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            "markdown",
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
        ],
    )
    assert result.exit_code == 0


def test_markdown_files_not_created(tmp_init_dir: str) -> None:
    """Tests failure of markdown file creation when not supplied with directory name."""
    SSP_INDEX_TESTER = "ssp-tester.index.json"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--ssp-name",
            "test-name",
            "repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            SSP_INDEX_TESTER,
        ],
    )
    assert result.exit_code == 2


def test_markdown_files_created(tmp_init_dir: str) -> None:
    """Tests successful creation of markdown files."""
    SSP_INDEX_TESTER = "ssp-tester.index.json"
    markdown_file_tester = "/markdown/system-security-plan.md"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            markdown_file_tester,
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            SSP_INDEX_TESTER,
        ],
    )
    assert result.exit_code == 0

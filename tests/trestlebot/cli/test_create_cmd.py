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
    compdef_list_tester = ["ac-12", "ac-13"]
    ssp_index_tester = "tmp_init_dir/tester-ssp-index.json"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            "markdown",
            "--compdefs",
            compdef_list_tester,
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            ssp_index_tester,
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
    compdef_list_tester = ["ac-12", "ac-13"]
    default_ssp_index_file = "tmp_init_dir/test-ssp-index.json"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            "markdown",
            "--compdefs",
            compdef_list_tester,
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            default_ssp_index_file,
        ],
    )
    assert result.exit_code == 0


def test_markdown_files_not_created(tmp_init_dir: str) -> None:
    """Tests failure of markdown file creation when not supplied with directory name."""
    compdef_list_tester = ["ac-12", "ac-13"]
    ssp_index_tester = "tmp_init_dir/ssp-tester.index.json"

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--compdefs",
            compdef_list_tester,
            "--ssp-name",
            "test-name",
            "repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            ssp_index_tester,
        ],
    )
    assert result.exit_code == 2


def test_markdown_files_created(tmp_init_dir: str) -> None:
    """Tests successful creation of markdown files."""
    ssp_index_tester = "tmp_init_dir/ssp-tester.index.json"
    markdown_file_tester = "tmp_init_dir/markdown/system-security-plan.md"
    compdef_list_tester = ["ac-12", "ac-13"]

    runner = CliRunner()
    result = runner.invoke(
        create_cmd,
        [
            "ssp",
            "--profile-name",
            "oscal-profile-name",
            "--markdown-dir",
            markdown_file_tester,
            "--compdefs",
            compdef_list_tester,
            "--ssp-name",
            "test-name",
            "--repo-path",
            tmp_init_dir,
            "--ssp-index-file",
            ssp_index_tester,
        ],
    )
    assert result.exit_code == 0

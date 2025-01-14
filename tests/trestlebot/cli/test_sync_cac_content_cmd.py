# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""" Unit test for sync-cac-content command"""
import pathlib
from typing import Tuple

from click.testing import CliRunner
from git import Repo

from tests.testutils import setup_for_catalog, setup_for_profile
from trestlebot.cli.commands.sync_cac_content import (
    sync_cac_content_cmd,
    sync_cac_content_profile_cmd,
)


test_product = "ocp4"
cac_content_test_data = pathlib.Path("tests/data/content").resolve()
test_prof_path = pathlib.Path("tests/data/json/").resolve()
test_prof = "simplified_nist_profile"
test_cat = "simplified_nist_catalog"
test_comp_path = f"component-definitions/{test_product}/component-definition.json"


def test_missing_required_option(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests missing required options in sync-cac-content command."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "--product",
            test_product,
            "--repo-path",
            str(repo_path.resolve()),
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
        ],
    )
    assert result.exit_code == 2


def test_sync_product_name(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac content product name to OSCAL component title ."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, test_cat, "catalog")
    setup_for_profile(repo_path, test_prof, "profile")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "--product",
            test_product,
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            cac_content_test_data,
            "--cac-profile",
            "cac-profile",
            "--oscal-profile",
            test_prof,
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
        ],
    )
    # Check the CLI sync-cac-content is successful
    assert result.exit_code == 0
    # Check if the component definition is created
    component_definition = repo_path.joinpath(test_comp_path)
    assert component_definition.exists()
    # Check if it populates the product name as the component title
    with open(component_definition, "r", encoding="utf-8") as file:
        content = file.read()
    assert '"title": "ocp4"' in content


def test_missing_required_option_profile(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests missing required options in sync-cac-content-profile subcommand."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    control_file_tester = "rhel9-control-file.yml"

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            "--control-file",
            control_file_tester,
            "--catalog",
            "catalog_tester",
            "--repo-path",
            str(repo_path.resolve()),
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
        ],
    )
    assert result.exit_code == 2


def test_created_oscal_profile(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests creation of OSCAL profile and change of .json title."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    tester_product = "rhel9"
    tester_catalog = "rhel9-catalog"
    setup_for_catalog(repo_path, test_cat, "catalog")
    # tester_profile = setup_for_profile(repo_path, test_prof, "profile")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            cac_content_test_data,
            "--product",
            tester_product,
            "--catalog",
            tester_catalog,
            "--control-file",
            "rhel9-control-file",
            "--filter-by-level",
            "high",
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
        ],
    )
    assert result.exit_code == 0
    # oscal_profile =
    # assert oscal_profile.exists()

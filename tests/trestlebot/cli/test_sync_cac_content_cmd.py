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
# test_profile_path = f"content/{test_product}/profiles/bsi-2022.profile"


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


# Working
def test_missing_required_profile_option(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests missing required options in sync-cac-content-profile subcommand."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    policy_id_test = "RHEL-9"

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "oscal-profile",
            "--policy-id",
            policy_id_test,
            "--oscal-catalog",
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


# Working
def test_invalid_subcommand() -> None:
    """Tests missing required options in sync-cac-content-profile subcommand."""

    runner = CliRunner()
    result = runner.invoke(sync_cac_content_cmd, ["Invalid"])
    assert result.exit_code == 2


# Need additional data
def test_created_oscal_profile(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests creation of OSCAL profile and change of .json title."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    policy_id_test = "OCP-4"
    test_profile = "simplified_nist_profile"
    setup_for_catalog(repo_path, test_cat, "catalog")
    setup_for_profile(repo_path, test_prof, "profile")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "oscal-profile",
            "--cac-content-root",
            cac_content_test_data,
            "--product",
            test_product,
            "--oscal-catalog",
            test_cat,
            "--policy-id",
            policy_id_test,
            "--filter-by-level",
            "high",
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
    assert result.exit_code == 0


def test_sync_profile_product_name(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac content product name to OSCAL component title ."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    setup_for_catalog(repo_path, test_cat, "catalog")
    setup_for_profile(repo_path, test_prof, "profile")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "oscal-profile",
            "--cac-content-root",
            cac_content_test_data,
            "product",
            test_product,
            "--oscal-catalog",
            test_prof,
            "--policy-id",
            "ac",
            "--filter-by-level",
            "high",
            "--repo-path",
            str(repo_path.resolve()),
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
    profile = repo_path.joinpath(test_prof_path)
    assert profile.exists()


def test_oscal_json_created(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests creation of OSCAL JSON file."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    catalog_tester = "simplified_nist_catalog.json"
    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "oscal-profile",
            "--cac-content-root",
            cac_content_test_data,
            "json",
            "--product",
            test_product,
            "--oscal-catalog",
            catalog_tester,
            "--repo-path",
            str(repo_path.resolve()),
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0

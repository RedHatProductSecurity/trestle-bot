# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""" Unit test for sync-cac-content command"""
import pathlib
from typing import Tuple

from click.testing import CliRunner
from git import Repo
from trestle.oscal.component import ComponentDefinition

from tests.testutils import setup_for_catalog, setup_for_profile
from trestlebot.cli.commands.sync_cac_content import (
    sync_cac_content_cmd,
    sync_cac_content_profile_cmd,
)


test_product = "rhel8"
# Note: data in test_content_dir is copied from content repo, PR:
# https://github.com/ComplianceAsCode/content/pull/12819
test_content_dir = pathlib.Path("tests/data/content_dir").resolve()
test_cac_profile = "products/rhel8/profiles/example.profile"
test_prof = "simplified_nist_profile"
test_cat = "simplified_nist_catalog"
test_comp_path = f"component-definitions/{test_product}/component-definition.json"
test_policy_id = "1234-levels"
test_level = "low"
# tester_prof_path = f"profiles/{policy_id}-{filter_by_level}/profiles.json"
# tester_prof_path = (
#     f"products/{test_product}/profiles/{test_policy_id}-{test_level}/profile.json"
# )
# test_prof_path = "1234-levels-low"


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


def test_non_existent_product(tmp_repo: Tuple[str, Repo]) -> None:
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_cmd,
        [
            "--product",
            "non-exist",
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            test_content_dir,
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
        ],
    )
    assert result.exit_code == 1


def test_sync_product(tmp_repo: Tuple[str, Repo]) -> None:
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
            test_content_dir,
            "--cac-profile",
            test_cac_profile,
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
    component_definition = repo_path.joinpath(test_comp_path)
    # Check if the component definition is created
    assert component_definition.exists()
    compdef = ComponentDefinition.oscal_read(component_definition)
    assert compdef.metadata.title == "Component definition for rhel8"
    assert len(compdef.components) == 1
    component = compdef.components[0]
    assert component.title == "rhel8"
    # Check rules component props
    assert len(component.props) == 6
    rule_ids = [p.value for p in component.props if p.name == "Rule_Id"]
    assert rule_ids == [
        "configure_crypto_policy",
        "file_groupownership_sshd_private_key",
        "sshd_set_keepalive",
    ]


def test_sync_product_create_validation_component(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac content to create validation component."""
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
            test_content_dir,
            "--cac-profile",
            test_cac_profile,
            "--oscal-profile",
            test_prof,
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
            "--component-definition-type",
            "validation",
        ],
    )
    # Check the CLI sync-cac-content is successful
    component_definition = repo_path.joinpath(test_comp_path)
    assert result.exit_code == 0
    # Check if the component definition is created
    assert component_definition.exists()
    compdef = ComponentDefinition.oscal_read(component_definition)
    component = compdef.components[0]
    assert len(component.props) == 12
    assert component.title == "openscap"
    assert component.type == "validation"


# Working
def test_missing_required_profile_option(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests missing required options in sync-cac-content-profile subcommand."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            "--cac-content-root",
            str(test_content_dir),
            "--product",
            test_product,
            # "--policy-id",
            # test_policy_id,
            "--oscal-catalog",
            test_cat,
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


def test_profile_supplied(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac profile content to create OSCAL Profile."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            str(test_content_dir),
            "--product",
            test_product,
            "--oscal-catalog",
            test_cat,
            "--policy-id",
            test_policy_id,
            "--filter-by-level",
            "medium",
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",  # Added after already working
        ],
    )
    assert result.exit_code == 0


# Profile test 2 - Need additional data
def test_created_oscal_profile(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests creation of OSCAL profile and change of .json title."""

    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    setup_for_catalog(repo_path, test_cat, "catalog")
    # test_catalog_path = repo_path.joinpath("catalogs", test_cat, "catalog.json")
    # tester_prof_path = (
    #     f"products/{test_product}/profiles/{test_policy_id}-{test_level}-profile.json"
    # )
    test_prof_path = f"profiles/{test_policy_id}-{test_level}/profile.json"

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            # "--repo-path",
            # str(repo_path.resolve()),
            "--cac-content-root",
            str(test_content_dir),
            "--product",
            test_product,
            "--oscal-catalog",
            test_cat,
            "--policy-id",
            test_policy_id,
            "--filter-by-level",
            test_level,
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
    # Using oscal_profile to define the path where OSCAL
    # Profile needs to be populated
    assert result.exit_code == 0
    profile = repo_path.joinpath(test_prof_path)
    assert profile.exists()
    # assert result.exit_code == 0
    # Checking if content exists in path

    # prof = Profile.oscal_read(profile)
    # assert prof.metadata.title == "Oscal Profile for rhel8 low baseline"
    # assert prof.imports[0].include_controls is not None

    # import_data = profile.imports[0]
    # assert profile.imports is not None
    # # Ensuring that the test catalog is used to get controls for OSCAL Profile
    # # Must have controls in include_controls
    # assert import_data.include_controls is not None


def test_sync_missing_profile_option(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac content profile command missing required option."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    # setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            # "--cac-content-root",
            # str(test_content_dir),
            "product",
            test_product,
            "--oscal-catalog",
            test_cat,
            "--policy-id",
            test_policy_id,
            "--filter-by-level",
            ["all"],
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
    assert result.exit_code == 2

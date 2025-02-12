# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Red Hat, Inc.

""" Unit tests for sync-cac-catalog command"""
import pathlib
from typing import Any, Generator, Tuple

from click import BaseCommand
from click.testing import CliRunner
from git import Repo
from ssg.controls import Policy
from trestle.oscal.catalog import Catalog, Control

from tests.testutils import TEST_DATA_DIR, setup_for_catalog
from trestlebot.cli.commands.sync_cac_catalog import sync_cac_catalog_cmd


test_product = "rhel8"
test_content_dir = TEST_DATA_DIR / "content_dir"
test_cac_control = "abcd-levels"
test_prof = "simplified_nist_profile"
test_cat = "simplified_nist_catalog"
test_comp_path = f"component-definitions/{test_product}/component-definition.json"
test_catalog_path = f"catalogs/{test_cat}/catalog.json"


def test_sync_catalog_create(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync CaC Profile to new OSCAL Catalog."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    assert isinstance(sync_cac_catalog_cmd, BaseCommand)
    result = runner.invoke(
        sync_cac_catalog_cmd,
        [
            "--cac-content-root",
            test_content_dir,
            "--repo-path",
            str(repo_path.resolve()),
            "--policy-id",
            test_cac_control,
            "--oscal-catalog",
            test_cac_control,
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
    assert result.exit_code == 0, result.output

    # Source
    policy = Policy(test_content_dir / "controls" / f"{test_cac_control}.yml")
    policy.load()

    # Destination
    # catalog_path = repo_path.joinpath(test_catalog_path)
    catalog_path = repo_path / "catalogs/abcd-levels/catalog.json"
    assert catalog_path.exists(), f"Catalog {catalog_path} must exist"
    catalog_obj = Catalog.oscal_read(catalog_path)
    assert catalog_obj.metadata.title == f"Catalog for {test_cac_control}"
    assert catalog_obj.metadata.oscal_version.__root__ == "1.1.2"
    assert catalog_obj.metadata.version == "REPLACE_ME"
    # (No top-level controls, all are in groups)
    assert sum([len(g.controls) for g in catalog_obj.groups]) == len(policy.controls)


def test_sync_catalog_create_real(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync Cac content product name to OSCAL component title ."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    assert isinstance(sync_cac_catalog_cmd, BaseCommand)
    ocp4_policy = "nist_ocp4"
    result = runner.invoke(
        sync_cac_catalog_cmd,
        [
            "--cac-content-root",
            test_content_dir,
            "--repo-path",
            str(repo_path.resolve()),
            "--policy-id",
            ocp4_policy,
            "--oscal-catalog",
            ocp4_policy,
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
    assert result.exit_code == 0, result.output

    # Source
    policy = Policy(test_content_dir / "controls/simplified_nist_ocp4.yml")
    policy.load()

    # Destination
    # catalog_path = repo_path.joinpath(test_catalog_path)
    catalog_path = repo_path / f"catalogs/{ocp4_policy}/catalog.json"
    assert catalog_path.exists(), f"Catalog {catalog_path} must exist"
    catalog_obj = Catalog.oscal_read(catalog_path)

    assert catalog_obj.metadata.title == f"Catalog for {ocp4_policy}"
    assert catalog_obj.metadata.oscal_version.__root__ == "1.1.2"
    assert catalog_obj.metadata.version == "REPLACE_ME"

    # (No top-level controls, all are in groups)
    def flatten_nested_controls(controls: Any) -> Generator[Control, None, None]:
        for control in controls:
            if control.controls:
                yield from flatten_nested_controls(control.controls)
            if isinstance(control, Control):
                yield control

    assert sum(1 for _ in flatten_nested_controls(catalog_obj.groups)) == len(
        policy.controls
    ), "Unexpected control count. Do you have multiple policy files with the same policy id?"


def test_sync_catalog_update(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests sync CaC Profile to existing OSCAL Catalog."""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, test_cat, "catalog")

    runner = CliRunner()
    assert isinstance(sync_cac_catalog_cmd, BaseCommand)
    test_cac_control = "nist_ocp4"
    result = runner.invoke(
        sync_cac_catalog_cmd,
        [
            "--cac-content-root",
            test_content_dir,
            "--repo-path",
            str(repo_path.resolve()),
            "--policy-id",
            test_cac_control,
            "--oscal-catalog",
            test_cat,
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    merged_catalog = Catalog.oscal_read(
        repo_path / "catalogs" / test_cat / "catalog.json"
    )
    assert (
        merged_catalog.metadata.title
        == "Trestle simplified: NIST Special Publication 800-53 Revision 5: "
        "Security and Privacy Controls for Federal Information Systems and Organizations"
    )
    assert merged_catalog.metadata.oscal_version.__root__ == "1.0.0"
    assert merged_catalog.metadata.version == "5.0.1"
    assert merged_catalog.groups[2].id == "au"

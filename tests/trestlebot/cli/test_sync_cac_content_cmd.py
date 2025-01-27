# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""" Unit test for sync-cac-content command"""
import pathlib
from typing import Tuple

from click.testing import CliRunner
from git import Repo
from trestle.common.const import REPLACE_ME
from trestle.oscal.component import ComponentDefinition

from tests.testutils import setup_for_catalog, setup_for_profile
from trestlebot.cli.commands.sync_cac_content import sync_cac_content_cmd


test_product = "rhel8"
# Note: data in test_content_dir is copied from content repo, PR:
# https://github.com/ComplianceAsCode/content/pull/12819
test_content_dir = pathlib.Path("tests/data/content_dir").resolve()
test_cac_profile = "products/rhel8/profiles/example.profile"
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
    # Check rules component props are added
    assert len(component.props) == 24
    rule_ids = [p.value for p in component.props if p.name == "Rule_Id"]
    assert sorted(rule_ids) == [
        "configure_crypto_policy",
        "file_groupownership_sshd_private_key",
        "sshd_set_keepalive",
    ]
    # Check parameters props are added
    param_ids = [p.value for p in component.props if p.name == "Parameter_Id"]
    assert sorted(list(set(param_ids))) == [
        "var_sshd_set_keepalive",
        "var_system_crypto_policy",
    ]

    # Check control_implementations are attached
    ci = component.control_implementations[0]
    assert ci.source == "trestle://profiles/simplified_nist_profile/profile.json"
    set_parameters = ci.set_parameters
    assert len(set_parameters) == 2
    set_params_ids = []
    set_params_dict = {}
    for param in set_parameters:
        set_params_ids.append(param.param_id)
        set_params_dict.update({param.param_id: param.values})
    assert sorted(set_params_ids) == [
        "var_sshd_set_keepalive",
        "var_system_crypto_policy",
    ]
    assert set_params_dict["var_sshd_set_keepalive"] == ["1"]
    assert set_params_dict["var_system_crypto_policy"] == ["fips"]

    # Check implemented requirements are populated
    for implemented_req in ci.implemented_requirements:
        if implemented_req.control_id == "ac-1":
            for prop in implemented_req.props:
                assert prop.value == "implemented"
                # Check mapping OscalStatus.IMPLEMENTED:CacStatus.AUTOMATED
                if prop.name == "implementation-status":
                    assert prop.value == "implemented"
            assert len(implemented_req.statements) == 2
            assert (
                implemented_req.statements[0].description
                == "AC-1(a) is an organizational control outside "
                "the scope of OpenShift configuration."
            )
            assert (
                implemented_req.statements[1].description
                == "AC-1(b) is an organizational control outside "
                "the scope of OpenShift configuration."
            )

        if implemented_req.control_id == "ac-2":
            for prop in implemented_req.props:
                assert prop.value == "alternative"
                # Check mapping OscalStatus.ALTERNATIVE:CacStatus.MANUAL
                if prop.name == "implementation-status":
                    assert prop.value == "alternative"
                    assert prop.remarks == REPLACE_ME


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
    assert len(component.props) == 30
    assert component.title == "openscap"
    assert component.type == "validation"

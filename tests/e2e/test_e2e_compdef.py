# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""E2E tests for commands for component definition authoring."""

import logging
import pathlib
import subprocess
from typing import Dict, Tuple

import pytest
from git.repo import Repo
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.profile import Profile

from tests.testutils import (
    build_test_command,
    load_from_json,
    setup_for_profile,
    setup_rules_view,
)
from trestlebot.const import (
    ERROR_EXIT_CODE,
    INVALID_ARGS_EXIT_CODE,
    RULES_VIEW_DIR,
    SUCCESS_EXIT_CODE,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

test_prof = "simplified_nist_profile"
test_filter_prof = "simplified_filter_profile"
test_comp_name = "test_comp"


@pytest.mark.slow
@pytest.mark.parametrize(
    "test_name, command_args, response",
    [
        (
            "success/happy path",
            {
                "branch": "test",
                "rules-view-path": RULES_VIEW_DIR,
                "committer-name": "test",
                "committer-email": "test@email.com",
            },
            SUCCESS_EXIT_CODE,
        ),
        (
            "success/happy path with model skipping",
            {
                "branch": "test",
                "rules-view-path": RULES_VIEW_DIR,
                "committer-name": "test",
                "committer-email": "test",
                "skip-items": test_comp_name,
            },
            SUCCESS_EXIT_CODE,
        ),
        (
            "failure/missing args",
            {
                "branch": "test",
                "rules-view-path": RULES_VIEW_DIR,
            },
            INVALID_ARGS_EXIT_CODE,
        ),
    ],
)
def test_rules_transform_e2e(
    tmp_repo: Tuple[str, Repo],
    podman_setup: Tuple[int, str],
    test_name: str,
    command_args: Dict[str, str],
    response: int,
) -> None:
    """Test the trestlebot rules transform command."""
    # Check that the container image was built successfully
    # and the mock server is running
    exit_code, image_name = podman_setup
    assert exit_code == 0

    logger.info(f"Running test: {test_name}")

    tmp_repo_str, repo = tmp_repo
    tmp_repo_path = pathlib.Path(tmp_repo_str)

    # Setup the rules directory
    setup_rules_view(tmp_repo_path, test_comp_name)

    remote_url = "http://localhost:8080/test.git"
    repo.create_remote("origin", url=remote_url)

    command = build_test_command(
        tmp_repo_str, "rules-transform", command_args, image_name
    )
    run_response = subprocess.run(command, capture_output=True)
    assert run_response.returncode == response

    # Check that the component definition was created
    if response == SUCCESS_EXIT_CODE:
        if "skip-items" in command_args:
            assert f"input: {test_comp_name}.csv" not in run_response.stdout.decode(
                "utf-8"
            )
        else:
            comp_path: pathlib.Path = ModelUtils.get_model_path_for_name_and_class(
                tmp_repo_path, test_comp_name, ComponentDefinition, FileContentType.JSON
            )
            assert comp_path.exists()
            assert f"input: {test_comp_name}.csv" in run_response.stdout.decode("utf-8")
        branch = command_args["branch"]
        assert (
            f"Changes pushed to {branch} successfully."
            in run_response.stdout.decode("utf-8")
        )


@pytest.mark.slow
@pytest.mark.parametrize(
    "test_name, command_args, response",
    [
        (
            "success/happy path",
            {
                "profile-name": test_prof,
                "component-title": "test-comp",
                "compdef-name": "test-compdef",
                "component-description": "test",
                "markdown-path": "markdown",
                "branch": "test",
                "committer-name": "test",
                "committer-email": "test@email.com",
            },
            SUCCESS_EXIT_CODE,
        ),
        (
            "success/happy path with filtering",
            {
                "profile-name": test_prof,
                "component-title": "test-comp",
                "compdef-name": "test-compdef",
                "component-description": "test",
                "markdown-path": "markdown",
                "branch": "test",
                "committer-name": "test",
                "committer-email": "test@email.com",
                "filter-by-profile": test_filter_prof,
            },
            SUCCESS_EXIT_CODE,
        ),
        (
            "failure/missing args",
            {
                "component-title": "test-comp",
                "compdef-name": "test-compdef",
                "component-description": "test",
                "markdown-path": "markdown",
                "branch": "test",
                "committer-name": "test",
                "committer-email": "test@email.com",
            },
            INVALID_ARGS_EXIT_CODE,
        ),
        (
            "failure/missing profile",
            {
                "profile-name": "fake",
                "component-title": "test-comp",
                "compdef-name": "test-compdef",
                "component-description": "test",
                "markdown-path": "markdown",
                "branch": "test",
                "committer-name": "test",
                "committer-email": "test@email.com",
            },
            ERROR_EXIT_CODE,
        ),
        (
            "failure/missing filter profile",
            {
                "profile-name": test_prof,
                "component-title": "test-comp",
                "compdef-name": "test-compdef",
                "component-description": "test",
                "markdown-path": "markdown",
                "branch": "test",
                "committer-name": "test",
                "committer-email": "test",
                "filter-by-profile": "fake",
            },
            ERROR_EXIT_CODE,
        ),
    ],
)
def test_create_cd_e2e(
    tmp_repo: Tuple[str, Repo],
    podman_setup: Tuple[int, str],
    test_name: str,
    command_args: Dict[str, str],
    response: int,
) -> None:
    """Test the trestlebot rules transform command."""
    # Check that the container image was built successfully
    # and the mock server is running
    exit_code, image_name = podman_setup
    assert exit_code == 0

    logger.info(f"Running test: {test_name}")

    tmp_repo_str, repo = tmp_repo
    tmp_repo_path = pathlib.Path(tmp_repo_str)

    # Load profiles into the environment
    _ = setup_for_profile(tmp_repo_path, test_prof, "")
    load_from_json(tmp_repo_path, test_filter_prof, test_filter_prof, Profile)

    remote_url = "http://localhost:8080/test.git"
    repo.create_remote("origin", url=remote_url)

    command = build_test_command(tmp_repo_str, "create-cd", command_args, image_name)
    run_response = subprocess.run(command, cwd=tmp_repo_path, capture_output=True)
    assert run_response.returncode == response

    # Check that all expected files were created
    if response == SUCCESS_EXIT_CODE:
        comp_path: pathlib.Path = ModelUtils.get_model_path_for_name_and_class(
            tmp_repo_path,
            command_args["compdef-name"],
            ComponentDefinition,
            FileContentType.JSON,
        )
        assert comp_path.exists()
        assert (tmp_repo_path / command_args["markdown-path"]).exists()
        assert (
            tmp_repo_path
            / RULES_VIEW_DIR
            / command_args["compdef-name"]
            / command_args["component-title"]
        ).exists()

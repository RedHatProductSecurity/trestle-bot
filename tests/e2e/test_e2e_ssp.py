# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""
E2E tests for SSP creation and autosync workflow.

Notes that this should be the only E2E for auto-syncing since the UX is the same for each model.
The SSP model is used here as a stand-in for all models because it is the most complex process.

The tests here are based on the following workflow:
1. Create new SSP
2. Autosync SSP to create initial Markdown
3. Run autosync again to check that no changes are pushed
4. Update the profile with sync-upstreams
5. Autosync again to check that the changes are pushed
"""

import logging
import os
import pathlib
import subprocess
from typing import Dict, Tuple

import pytest
from git.repo import Repo
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.ssp import SystemSecurityPlan

from tests.e2e.e2e_testutils import E2ETestRunner
from tests.testutils import clean, prepare_upstream_repo, setup_for_ssp
from trestlebot.const import ERROR_EXIT_CODE, SUCCESS_EXIT_CODE
from trestlebot.tasks.authored.ssp import SSPIndex


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

test_prof = "simplified_nist_profile"
test_comp_name = "test_comp"
test_ssp_md = "md_ssp"
test_ssp_name = "test_ssp"


@pytest.mark.slow
@pytest.mark.parametrize(
    "test_name, command_args, response, skip_create",
    [
        (
            "success/happy path",
            {
                "branch": "test",
                "markdown-path": test_ssp_md,
                "oscal-model": "ssp",
                "committer-name": "test",
                "committer-email": "test@email.com",
                "ssp-index": "ssp-index.json",
            },
            SUCCESS_EXIT_CODE,
            False,
        ),
        (
            "failure/missing-ssp-index",
            {
                "branch": "test",
                "markdown-path": test_ssp_md,
                "oscal-model": "ssp",
                "committer-name": "test",
                "committer-email": "test@email.com",
            },
            ERROR_EXIT_CODE,
            True,
        ),
    ],
)
def test_ssp_editing_e2e(
    tmp_repo: Tuple[str, Repo],
    e2e_runner: E2ETestRunner,
    test_name: str,
    command_args: Dict[str, str],
    response: int,
    skip_create: bool,
) -> None:
    """Test the trestlebot autosync command with SSPs."""
    logger.info(f"Running test: {test_name}")

    tmp_repo_str, _ = tmp_repo
    tmp_repo_path = pathlib.Path(tmp_repo_str)

    args = setup_for_ssp(tmp_repo_path, test_prof, [test_comp_name], test_ssp_md)

    # Create or generate the SSP
    if not skip_create:
        create_args: Dict[str, str] = {
            "markdown-path": command_args["markdown-path"],
            "branch": command_args["branch"],
            "committer-name": command_args["committer-name"],
            "committer-email": command_args["committer-email"],
            "ssp-name": test_ssp_name,
            "profile-name": test_prof,
            "compdefs": test_comp_name,
        }
        command = e2e_runner.build_test_command(
            tmp_repo_str,
            "create-ssp",
            create_args,
        )
        exit_code, _ = e2e_runner.invoke_command(command)
        assert exit_code == response
        assert (tmp_repo_path / command_args["markdown-path"]).exists()

        # Make a change to the SSP
        ssp, ssp_path = ModelUtils.load_model_for_class(
            tmp_repo_path,
            test_ssp_name,
            SystemSecurityPlan,
            FileContentType.JSON,
        )
        ssp.metadata.title = "New Title"
        ssp.oscal_write(ssp_path)
    else:
        ssp_generate = SSPGenerate()
        assert ssp_generate._run(args) == 0

    command = e2e_runner.build_test_command(tmp_repo_str, "autosync", command_args)
    run_response = subprocess.run(command, capture_output=True)
    assert run_response.returncode == response

    # Check that the ssp was pushed to the remote
    if response == SUCCESS_EXIT_CODE:
        branch = command_args["branch"]
        assert (
            f"Changes pushed to {branch} successfully."
            in run_response.stdout.decode("utf-8")
        )

        # Check that the correct files are present with the correct content
        index_path = os.path.join(tmp_repo_str, "ssp-index.json")
        ssp_index = SSPIndex(index_path)
        assert ssp_index.get_profile_by_ssp(test_ssp_name) == test_prof
        assert ssp_index.get_comps_by_ssp(test_ssp_name) == [test_comp_name]
        assert ssp_index.get_leveraged_by_ssp(test_ssp_name) is None
        assert ssp_path.exists()

        # Check that if run again, the ssp is not pushed again
        command = e2e_runner.build_test_command(tmp_repo_str, "autosync", command_args)
        exit_code, response_stdout = e2e_runner.invoke_command(command)
        assert exit_code == SUCCESS_EXIT_CODE
        assert "Nothing to commit" in response_stdout

        # Check that if the upstream profile is updated, the ssp is updated
        local_upstream_path = prepare_upstream_repo()
        upstream_repos_arg = f"{e2e_runner.UPSTREAM_REPO}@main"
        upstream_command_args = {
            "branch": command_args["branch"],
            "committer-name": command_args["committer-name"],
            "committer-email": command_args["committer-email"],
            "sources": upstream_repos_arg,
        }
        command = e2e_runner.build_test_command(
            tmp_repo_str,
            "sync-upstreams",
            upstream_command_args,
            local_upstream_path,
        )
        exit_code, response_stdout = e2e_runner.invoke_command(command)
        assert exit_code == SUCCESS_EXIT_CODE
        assert (
            f"Changes pushed to {command_args['branch']} successfully."
            in run_response.stdout.decode("utf-8")
        )

        # Autosync again to check that the ssp is updated
        command = e2e_runner.build_test_command(tmp_repo_str, "autosync", command_args)
        exit_code, response_stdout = e2e_runner.invoke_command(command)
        assert exit_code == SUCCESS_EXIT_CODE
        assert (
            f"Changes pushed to {command_args['branch']} successfully."
            in response_stdout
        )

        # Clean up the upstream repo
        clean(local_upstream_path, None)

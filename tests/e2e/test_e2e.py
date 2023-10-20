#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import pathlib
import subprocess
from typing import Dict, List, Tuple

import pytest
from git.repo import Repo
from trestle.core.commands.init import InitCmd

from tests.conftest import YieldFixture
from tests.testutils import args_dict_to_list, setup_rules_view
from trestlebot.const import RULES_VIEW_DIR


image_name = "localhost/trestlebot:latest"
mock_server_image_name = "localhost/mock-server:latest"
pod_name = "trestlebot-e2e-pod"
e2e_context = "tests/e2e"
file = "Dockerfile"


# Define test cases and expected outcomes
test_cases: List[Tuple[Dict[str, str], int]] = [
    (
        {
            "branch": "test",
            "rules-view-path": RULES_VIEW_DIR,
            "committer-name": "test",
            "committer-email": "test@email.com",
            "file-patterns": ".",
        },
        0,
    ),
    (
        {
            "branch": "test",
            "rules-view-path": RULES_VIEW_DIR,
            "file-patterns": ".",
        },
        2,
    ),
]


def build_image_command(data_path: str, command_args: Dict[str, str]) -> List[str]:
    """Build a command to be run in the shell."""
    return [
        "podman",
        "run",
        "--pod",
        pod_name,
        "--entrypoint",
        "trestlebot-rules-transform",
        "--rm",
        "-v",
        f"{data_path}:/trestle",
        "-w",
        "/trestle",
        image_name,
        *args_dict_to_list(command_args),
    ]


@pytest.fixture(scope="module")
def podman_setup() -> YieldFixture[int]:
    """Build the trestlebot container image and run the mock server in a pod."""
    # Build the container image
    subprocess.run(
        [
            "podman",
            "build",
            "-f",
            file,
            "-t",
            image_name,
        ],
        check=True,
    )

    # Build mock server container image
    subprocess.run(
        [
            "podman",
            "build",
            "-f",
            f"{e2e_context}/{file}",
            "-t",
            mock_server_image_name,
            e2e_context,
        ],
        check=True,
    )

    # Create a pod
    response = subprocess.run(
        ["podman", "play", "kube", f"{e2e_context}/play-kube.yml"], check=True
    )
    yield response.returncode

    # Clean up the container image, pod and mock server
    try:
        subprocess.run(
            ["podman", "play", "kube", "--down", f"{e2e_context}/play-kube.yml"],
            check=True,
        )
        subprocess.run(["podman", "rmi", image_name], check=True)
        subprocess.run(["podman", "rmi", mock_server_image_name], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clean up podman resources: {e}")


# Run each test case
@pytest.mark.slow
@pytest.mark.parametrize("command_args, response", test_cases)
def test_rules_transform_e2e(
    tmp_repo: Tuple[str, Repo],
    podman_setup: int,
    command_args: Dict[str, str],
    response: int,
) -> None:
    """Test the trestlebot rules transform command."""
    # Check that the container image was built successfully
    # and the mock server is running
    assert podman_setup == 0

    tmp_repo_str, repo = tmp_repo

    tmp_repo_path = pathlib.Path(tmp_repo_str)

    # Create a trestle workspace in the temporary git repository
    args = argparse.Namespace(
        verbose=0,
        trestle_root=tmp_repo_path,
        full=True,
        local=False,
        govdocs=False,
    )
    init = InitCmd()
    init._run(args)

    # Setup the rules directory
    setup_rules_view(tmp_repo_path, "test-comp")

    remote_url = "http://localhost:8080/test.git"
    repo.create_remote("origin", url=remote_url)

    # Build the command to be run in the shell
    command = build_image_command(tmp_repo_str, command_args)

    # Run the command
    run_response = subprocess.run(command, cwd=tmp_repo_path)

    # Get subprocess response
    assert run_response.returncode == response

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Helper functions and class for e2e setup, execution, and teardown."""

import os
import pathlib
import subprocess
from typing import Dict, List, Optional, Tuple

from tests.testutils import args_dict_to_list


class E2ETestRunner:
    """Class to run e2e tests."""

    TRESTLEBOT_TEST_IMAGE_NAME = "localhost/trestlebot:latest"
    MOCK_SERVER_IMAGE_NAME = "localhost/mock-server:latest"
    TRESTLEBOT_TEST_POD_NAME = "trestlebot-e2e-pod"
    E2E_BUILD_CONTEXT = "tests/e2e"
    CONTAINER_FILE_NAME = "Dockerfile"
    UPSTREAM_REPO = "/upstream"

    def __init__(self) -> None:
        """Initialize the class."""
        self.trestlebot_image = os.environ.get(
            "TRESTLEBOT_IMAGE", E2ETestRunner.TRESTLEBOT_TEST_IMAGE_NAME
        )
        self.cleanup_trestlebot_image = False
        self.cleanup_mock_server_image = False

    def setup(self) -> None:
        """
        Build the trestlebot container image and run the mock server in a pod.

        Yields:
            Tuple[int, str]: The return code from the podman play command and the trestlebot image name.
        """
        try:
            self.cleanup_trestlebot_image = self.build_test_image(self.trestlebot_image)
            self.cleanup_mock_server_image = self.build_test_image(
                E2ETestRunner.MOCK_SERVER_IMAGE_NAME,
                f"{E2ETestRunner.E2E_BUILD_CONTEXT}/{E2ETestRunner.CONTAINER_FILE_NAME}",
                E2ETestRunner.E2E_BUILD_CONTEXT,
            )

            # Create a pod
            subprocess.run(
                [
                    "podman",
                    "play",
                    "kube",
                    f"{E2ETestRunner.E2E_BUILD_CONTEXT}/play-kube.yml",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set up podman resources: {e}")

    def teardown(self) -> None:
        """Clean up the container image, pod and mock server"""
        try:
            subprocess.run(
                [
                    "podman",
                    "play",
                    "kube",
                    "--down",
                    f"{E2ETestRunner.E2E_BUILD_CONTEXT}/play-kube.yml",
                ],
                check=True,
            )
            if self.cleanup_trestlebot_image:
                subprocess.run(["podman", "rmi", self.trestlebot_image], check=True)
            if self.cleanup_mock_server_image:
                subprocess.run(
                    ["podman", "rmi", E2ETestRunner.MOCK_SERVER_IMAGE_NAME], check=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clean up podman resources: {e}")

    @staticmethod
    def _image_exists(image_name: str) -> bool:
        """Check if the image already exists."""
        try:
            subprocess.check_output(["podman", "image", "inspect", image_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def build_test_image(
        self,
        image_name: str,
        container_file: str = CONTAINER_FILE_NAME,
        build_context: str = ".",
    ) -> bool:
        """
        Build an image for testing image.

        Returns:
            Returns true if the image was built, false if it already exists.
        """
        if not self._image_exists(image_name):
            subprocess.run(
                [
                    "podman",
                    "build",
                    "-f",
                    container_file,
                    "-t",
                    image_name,
                    build_context,
                ],
                check=True,
            )
            return True
        return False

    def build_test_command(
        self,
        data_path: str,
        command_name: str,
        command_args: Dict[str, str],
        upstream_repo: str = "",
    ) -> List[str]:
        """
        Build a command to be run in the shell for trestlebot

        Args:
            data_path (str): Path to the data directory. This is the working directory/trestle_root.
            command_name (str): Name of the command to run. It should be a trestlebot command.
            command_args (Dict[str, str]): Arguments to pass to the command
            image_name (str, optional): Name of the image to run. Defaults to TRESTLEBOT_TEST_IMAGE_NAME.
            upstream_repo (str, optional): Path to the upstream repo. Defaults to "" and is not mounted.

        Returns:
            List[str]: Command to be run in the shell
        """
        command = [
            "podman",
            "run",
            "--pod",
            E2ETestRunner.TRESTLEBOT_TEST_POD_NAME,
            "--entrypoint",
            f"trestlebot-{command_name}",
            "--rm",
        ]

        # Add mounts
        if upstream_repo:
            # Add a volume and mount it to the container
            command.extend(["-v", f"{upstream_repo}:{E2ETestRunner.UPSTREAM_REPO}"])

        command.extend(
            [
                "-v",
                f"{data_path}:/trestle",
                "-w",
                "/trestle",
                self.trestlebot_image,
                *args_dict_to_list(command_args),
            ]
        )
        return command

    def invoke_command(
        self, command: List[str], working_dir: Optional[pathlib.Path] = None
    ) -> Tuple[int, str]:
        """
        Invoke a command in the e2e test.

        Args:
            command (str): Command to run in the shell

        Returns:
            Tuple[int, str]: Return code and stdout of the command
        """
        result = subprocess.run(command, cwd=working_dir, capture_output=True)
        return result.returncode, result.stdout.decode("utf-8")

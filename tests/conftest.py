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

"""Common test fixtures."""

import argparse
import logging
import os
import pathlib
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Dict, Generator, Tuple, TypeVar

import pytest
from git.repo import Repo
from trestle.common.err import TrestleError
from trestle.core.commands.init import InitCmd

from tests.testutils import (
    CONTAINER_FILE_NAME,
    E2E_BUILD_CONTEXT,
    MOCK_SERVER_IMAGE_NAME,
    TRESTLEBOT_TEST_IMAGE_NAME,
    build_test_image,
    clean,
)
from trestlebot import const
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Parameter,
    Profile,
    TrestleRule,
)


T = TypeVar("T")
YieldFixture = Generator[T, None, None]

_TEST_CONTENTS = """
test file
"""
_TEST_FILENAME = "test.txt"
_TEST_PREFIX = "trestlebot_tests"


@pytest.fixture(scope="function")
def tmp_repo() -> YieldFixture[Tuple[str, Repo]]:
    """Create a temporary git repository"""
    with TemporaryDirectory(prefix=_TEST_PREFIX) as tmpdir:
        test_file = os.path.join(tmpdir, _TEST_FILENAME)
        with open(test_file, "x", encoding="utf8") as file:
            file.write(_TEST_CONTENTS)
        repo = Repo.init(tmpdir)
        with repo.config_writer() as config:
            config.set_value("user", "email", "test@example.com")
            config.set_value("user", "name", "Test User")
        repo.git.add(all=True)
        repo.index.commit("Initial commit")
        yield tmpdir, repo

        try:
            clean(tmpdir, repo)
        except Exception as e:
            logging.error(f"Failed to clean up temporary git repository: {e}")


@pytest.fixture(scope="function")
def tmp_trestle_dir() -> YieldFixture[str]:
    """Create an initialized temporary trestle directory"""
    with TemporaryDirectory(prefix=_TEST_PREFIX) as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        try:
            args = argparse.Namespace(
                verbose=0,
                trestle_root=tmp_path,
                full=True,
                local=False,
                govdocs=False,
            )
            init = InitCmd()
            init._run(args)
        except Exception as e:
            raise TrestleError(
                f"Initialization failed for temporary trestle directory: {e}."
            )
        yield tmpdir


@pytest.fixture(scope="function")
def valid_rule_data() -> Dict[str, Any]:
    return {
        const.RULE_INFO_TAG: {
            const.NAME: "example_rule_1",
            const.DESCRIPTION: "My rule description for example rule 1",
            const.PROFILE: {
                const.DESCRIPTION: "Simple NIST Profile",
                const.HREF: "profiles/simplified_nist_profile/profile.json",
            },
            const.PARAMETER: {
                const.NAME: "prm_1",
                const.DESCRIPTION: "prm_1 description",
                const.ALTERNATIVE_VALUES: {
                    "default": "5%",
                    "5pc": "5%",
                    "10pc": "10%",
                    "15pc": "15%",
                    "20pc": "20%",
                },
                const.DEFAULT_VALUE: "5%",
            },
        }
    }


@pytest.fixture(scope="function")
def invalid_param_rule_data() -> Dict[str, Any]:
    return {
        const.RULE_INFO_TAG: {
            const.NAME: "example_rule_1",
            const.DESCRIPTION: "My rule description for example rule 1",
            const.PROFILE: {
                const.DESCRIPTION: "Simple NIST Profile",
                const.HREF: "profiles/simplified_nist_profile/profile.json",
            },
            const.PARAMETER: {
                const.NAME: "prm_1",
                const.DESCRIPTION: "prm_1 description",
                const.ALTERNATIVE_VALUES: {
                    "5pc": "5%",
                    "10pc": "10%",
                    "15pc": "15%",
                    "20pc": "20%",
                },
                const.DEFAULT_VALUE: "5%",
            },
        }
    }


@pytest.fixture(scope="function")
def missing_key_rule_data() -> Dict[str, Any]:
    return {
        const.RULE_INFO_TAG: {
            const.DESCRIPTION: "My rule description for example rule 1",
            const.PROFILE: {
                const.DESCRIPTION: "Simple NIST Profile",
                const.HREF: "profiles/simplified_nist_profile/profile.json",
            },
            const.PARAMETER: {
                const.NAME: "prm_1",
                const.DESCRIPTION: "prm_1 description",
                const.ALTERNATIVE_VALUES: {
                    "default": "5%",
                    "5pc": "5%",
                    "10pc": "10%",
                    "15pc": "15%",
                    "20pc": "20%",
                },
                const.DEFAULT_VALUE: "5%",
            },
        }
    }


@pytest.fixture(scope="function")
def test_rule() -> TrestleRule:
    test_trestle_rule: TrestleRule = TrestleRule(
        name="test",
        description="test",
        component=ComponentInfo(name="test_comp", type="test", description="test"),
        parameter=Parameter(
            name="test",
            description="test",
            alternative_values={},
            default_value="test",
        ),
        profile=Profile(
            description="test", href="test", include_controls=[Control(id="ac-1")]
        ),
    )
    return test_trestle_rule


# E2E test fixtures


@pytest.fixture(scope="package")
def podman_setup() -> YieldFixture[Tuple[int, str]]:
    """
    Build the trestlebot container image and run the mock server in a pod.

    Yields:
        Tuple[int, str]: The return code from the podman play command and the trestlebot image name.
    """

    # Get the image information from the environment, if present
    trestlebot_image = os.environ.get("TRESTLEBOT_IMAGE", TRESTLEBOT_TEST_IMAGE_NAME)

    cleanup_trestlebot_image = build_test_image(trestlebot_image)
    cleanup_mock_server_image = build_test_image(
        MOCK_SERVER_IMAGE_NAME,
        f"{E2E_BUILD_CONTEXT}/{CONTAINER_FILE_NAME}",
        E2E_BUILD_CONTEXT,
    )

    # Create a pod
    response = subprocess.run(
        ["podman", "play", "kube", f"{E2E_BUILD_CONTEXT}/play-kube.yml"], check=True
    )
    yield response.returncode, trestlebot_image

    # Clean up the container image, pod and mock server
    try:
        subprocess.run(
            ["podman", "play", "kube", "--down", f"{E2E_BUILD_CONTEXT}/play-kube.yml"],
            check=True,
        )
        if cleanup_trestlebot_image:
            subprocess.run(["podman", "rmi", trestlebot_image], check=True)
        if cleanup_mock_server_image:
            subprocess.run(["podman", "rmi", MOCK_SERVER_IMAGE_NAME], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clean up podman resources: {e}")

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

"""Test fixtures"""

import argparse
import os
import pathlib
from tempfile import TemporaryDirectory
from typing import Generator, Tuple, TypeVar

import pytest
from git.repo import Repo
from trestle.common.err import TrestleError
from trestle.core.commands.init import InitCmd


T = TypeVar("T")

YieldFixture = Generator[T, None, None]

_TEST_CONTENTS = """
test file
"""

_TEST_FILENAME = "test.txt"


@pytest.fixture
def tmp_repo() -> YieldFixture[Tuple[str, Repo]]:
    """Create a temporary git repository"""
    with TemporaryDirectory(prefix="trestlebot_tests") as tmpdir:
        with open(os.path.join(tmpdir, _TEST_FILENAME), "x", encoding="utf8") as file:
            file.write(_TEST_CONTENTS)
        repo = Repo.init(tmpdir)
        with repo.config_writer() as config:
            config.set_value("user", "email", "test@example.com")
            config.set_value("user", "name", "Test User")
        repo.git.add(all=True)
        repo.index.commit("Initial commit")
        yield tmpdir, repo


@pytest.fixture
def tmp_trestle_dir() -> YieldFixture[str]:
    """Create an initialized temporary trestle directory"""
    with TemporaryDirectory(prefix="trestlebot_tests") as tmpdir:
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

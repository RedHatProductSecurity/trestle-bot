# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""E2E test fixtures."""

import pytest

from tests.conftest import YieldFixture
from tests.e2e.e2e_testutils import E2ETestRunner


@pytest.fixture(scope="package")
def e2e_runner() -> YieldFixture[E2ETestRunner]:
    """Fixture for running e2e tests."""
    runner = E2ETestRunner()
    runner.setup()
    yield runner
    runner.teardown()

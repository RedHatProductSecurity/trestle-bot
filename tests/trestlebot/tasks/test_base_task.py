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

"""Test workspace filtering logic."""

import pathlib
from typing import List

import pytest

from trestlebot.tasks.base_task import ModelFilter


@pytest.mark.parametrize(
    "skip_list, include_list, model_name, expected",
    [
        [["simplified_nist_catalog"], [], "simplified_nist_catalog", True],
        [[], ["simplified_nist_catalog"], "simplified_nist_catalog", False],
        [["simplified*"], ["*"], "simplified_nist_catalog", True],
        [
            ["simplified_nist_catalog"],
            ["simplified*"],
            "simplified_nist_profile",
            False,
        ],
        [[], [], "simplified_nist_catalog", True],
        [[], ["*"], "simplified_nist_catalog", False],
    ],
)
def test_is_skipped(
    skip_list: List[str], include_list: List[str], model_name: str, expected: str
) -> None:
    """Test skip logic."""
    model_path = pathlib.Path(model_name)
    model_filter = ModelFilter(skip_list, include_list)
    assert model_filter.is_skipped(model_path) == expected

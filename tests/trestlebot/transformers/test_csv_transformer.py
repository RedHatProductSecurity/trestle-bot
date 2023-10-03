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

"""Test for CSV Transformer."""

import csv
import pathlib
from typing import List

import pytest

from trestlebot.transformers.csv_transformer import CSVBuilder
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Parameter,
    Profile,
    TrestleRule,
)


test_comp = "my comp"


def test_csv_builder(tmp_trestle_dir: str) -> None:
    """Test CSV builder on a happy path"""
    test_trestle_rule: TrestleRule = TrestleRule(
        name="test",
        description="test",
        component=ComponentInfo(name=test_comp, type="test", description="test"),
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
    csv_builder = CSVBuilder()
    csv_builder.add_row(test_trestle_rule)

    assert len(csv_builder._rows) == 1
    row = csv_builder._rows[0]
    assert row["Rule_Id"] == test_trestle_rule.name
    assert row["Rule_Description"] == test_trestle_rule.description
    assert row["Component_Title"] == test_trestle_rule.component.name
    assert row["Component_Type"] == test_trestle_rule.component.type
    assert row["Component_Description"] == test_trestle_rule.component.description
    assert row["Control_Id_List"] == "ac-1"
    assert row["Parameter_Id"] == test_trestle_rule.parameter.name  # type: ignore
    assert row["Parameter_Description"] == test_trestle_rule.parameter.description  # type: ignore
    assert row["Parameter_Value_Alternatives"] == "{}"
    assert row["Parameter_Value_Default"] == test_trestle_rule.parameter.default_value  # type: ignore
    assert row["Profile_Description"] == test_trestle_rule.profile.description
    assert row["Profile_Source"] == test_trestle_rule.profile.href

    trestle_root = pathlib.Path(tmp_trestle_dir)
    tmp_csv_path = trestle_root.joinpath("test.csv")
    csv_builder.write_to_file(tmp_csv_path)

    assert tmp_csv_path.exists()

    first_row: List[str] = []
    with open(tmp_csv_path, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile)
        first_row = next(csv_reader)

    for column in csv_builder._csv_columns.get_required_column_names():
        assert column in first_row


def test_validate_row() -> None:
    """Test validate row with an invalid row."""
    row = {"Rule_Id": "test"}
    csv_builder = CSVBuilder()
    with pytest.raises(RuntimeError, match="Row missing key: *"):
        csv_builder.validate_row(row)
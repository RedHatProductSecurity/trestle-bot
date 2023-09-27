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

"""Test for YAML to CSV Transformer."""

import csv
import pathlib
from typing import List

import pytest

from tests.testutils import YAML_TEST_DATA_PATH
from trestlebot.transformers.yaml_to_csv import (
    ComponentInfo,
    Control,
    CSVBuilder,
    Parameter,
    Profile,
    RulesYAMLTransformer,
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
            name="test", description="test", alternative_values={}, default_value="test"
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


def test_rule_transformer() -> None:
    """Test rule transformer."""
    # load rule from path and close the file
    # get the file info as a string
    rule_path = YAML_TEST_DATA_PATH / "test_complete_rule.yaml"
    rule_file = open(rule_path, "r")
    rule_file_info = rule_file.read()
    rule_file.close()

    transformer = RulesYAMLTransformer()
    rule = transformer.transform(rule_file_info)

    assert rule.name == "example_rule_1"
    assert rule.description == "My rule description for example rule 1"
    assert rule.component.name == "Component 1"
    assert rule.component.type == "service"
    assert rule.component.description == "Component 1 description"
    assert rule.parameter is not None
    assert rule.parameter.name == "prm_1"
    assert rule.parameter.description == "prm_1 description"
    assert rule.parameter.alternative_values == {
        "default": "5%",
        "5pc": "5%",
        "10pc": "10%",
        "15pc": "15%",
        "20pc": "20%",
    }
    assert rule.parameter.default_value == "5%"
    assert rule.profile.description == "Simple NIST Profile"
    assert rule.profile.href == "profiles/simplified_nist_profile/profile.json"


def test_rules_transform_with_invalid_rule() -> None:
    """Test rules transform with invalid rule."""
    # Generate test json string
    test_string = '{"test_json": "test"}'
    transformer = RulesYAMLTransformer()

    with pytest.raises(
        RuntimeError, match="Missing key in YAML file: 'x-trestle-rule-info'"
    ):
        transformer.transform(test_string)

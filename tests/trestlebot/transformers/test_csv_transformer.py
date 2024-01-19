# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Test for CSV Transformer."""

import csv
import pathlib
from typing import List

import pytest

from trestlebot.transformers.csv_transformer import (
    CSVBuilder,
    FromRulesCSVTransformer,
    ToRulesCSVTransformer,
)
from trestlebot.transformers.trestle_rule import TrestleRule


def test_csv_builder(test_rule: TrestleRule, tmp_trestle_dir: str) -> None:
    """Test CSV builder on a happy path"""

    csv_builder = CSVBuilder()
    csv_builder.add_row(test_rule)

    assert len(csv_builder._rows) == 1
    row = csv_builder._rows[0]
    assert row["Rule_Id"] == test_rule.name
    assert row["Rule_Description"] == test_rule.description
    assert row["Component_Title"] == test_rule.component.name
    assert row["Component_Type"] == test_rule.component.type
    assert row["Component_Description"] == test_rule.component.description
    assert row["Control_Id_List"] == "ac-1"
    assert row["Parameter_Id"] == test_rule.parameter.name  # type: ignore
    assert row["Parameter_Description"] == test_rule.parameter.description  # type: ignore
    assert row["Parameter_Value_Alternatives"] == "{}"
    assert row["Parameter_Value_Default"] == test_rule.parameter.default_value  # type: ignore
    assert row["Profile_Description"] == test_rule.profile.description
    assert row["Profile_Source"] == test_rule.profile.href

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


def test_read_write_integration(test_rule: TrestleRule) -> None:
    """Test read/write integration."""
    from_rules_transformer = FromRulesCSVTransformer()
    to_rules_transformer = ToRulesCSVTransformer()

    csv_row_data = from_rules_transformer.transform(test_rule)
    read_rule = to_rules_transformer.transform(csv_row_data)

    assert read_rule == test_rule

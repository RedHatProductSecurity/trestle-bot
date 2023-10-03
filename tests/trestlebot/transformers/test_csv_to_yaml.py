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

import csv
import pathlib
from dataclasses import fields

import pytest
import ruamel.yaml as yaml

from trestlebot.transformers.csv_to_yaml import YAMLBuilder
from trestlebot.transformers.trestle_rule import TrestleRule


@pytest.fixture(scope="function")
def setup_yaml_builder() -> YAMLBuilder:
    return YAMLBuilder()


def write_sample_csv(csv_file: pathlib.Path) -> None:
    with open(csv_file, "w", newline="") as csvfile:
        fieldnames = [
            "RULE_ID",
            "RULE_DESCRIPTION",
            "PROFILE_DESCRIPTION",
            "PROFILE_SOURCE",
            "CONTROL_ID_LIST",
            "COMPONENT_TITLE",
            "COMPONENT_DESCRIPTION",
            "COMPONENT_TYPE",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "RULE_ID": "Rule1",
                "RULE_DESCRIPTION": "Description1",
                "PROFILE_DESCRIPTION": "ProfileDesc1",
                "PROFILE_SOURCE": "http://example.com",
                "CONTROL_ID_LIST": "C1, C2",
                "COMPONENT_TITLE": "Component1",
                "COMPONENT_DESCRIPTION": "ComponentDesc1",
                "COMPONENT_TYPE": "Type1",
            }
        )


def test_read_from_csv(setup_yaml_builder: YAMLBuilder, tmp_trestle_dir: str) -> None:
    csv_file = pathlib.Path(tmp_trestle_dir) / "test.csv"
    write_sample_csv(csv_file)
    setup_yaml_builder.read_from_csv(csv_file)
    assert len(setup_yaml_builder._rules) == 1


def test_write_to_yaml(setup_yaml_builder: YAMLBuilder, tmp_trestle_dir: str) -> None:
    csv_file = pathlib.Path(tmp_trestle_dir) / "test.csv"
    yaml_file = pathlib.Path(tmp_trestle_dir) / "test.yaml"
    write_sample_csv(csv_file)
    setup_yaml_builder.read_from_csv(csv_file)
    setup_yaml_builder.write_to_yaml(yaml_file)
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    assert len(data) == 1


def test_write_empty_trestle_rule_keys(
    setup_yaml_builder: YAMLBuilder, tmp_trestle_dir: str
) -> None:
    yaml_file = pathlib.Path(tmp_trestle_dir) / "test.yaml"
    setup_yaml_builder.write_empty_trestle_rule_keys(yaml_file)
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    assert all(value == "" for value in data.values())
    expected_keys = {field.name for field in fields(TrestleRule)}
    assert expected_keys == set(data.keys())

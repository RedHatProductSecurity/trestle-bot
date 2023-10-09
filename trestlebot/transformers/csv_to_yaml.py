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
"""CSV to YAML converter for rule authoring."""

import csv
import pathlib
from typing import List

from trestlebot.transformers.csv_transformer import ToRulesCSVTransformer
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Profile,
    TrestleRule,
)
from trestlebot.transformers.yaml_transformer import FromRulesYAMLTransformer


class YAMLBuilder:
    """Build Rules View in YAML from a CSV file."""

    def __init__(self) -> None:
        """Initialize."""
        self._rules: List[TrestleRule] = []
        self._yaml_transformer = FromRulesYAMLTransformer()
        self._csv_transformer = ToRulesCSVTransformer()

    def read_from_csv(self, filepath: pathlib.Path) -> None:
        """Read from a CSV file and populate self._rules."""
        try:
            with open(filepath, mode="r", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self._rules.append(self._csv_transformer.transform(row))
        except FileNotFoundError:
            raise CSVReadError(f"File not found: {filepath}")
        except csv.Error as e:
            raise CSVReadError(f"CSV reading error: {e}")

    def write_to_yaml(self, filepath: pathlib.Path) -> None:
        """Write the rules to a YAML file."""
        try:
            with open(filepath, mode="w") as yaml_file:
                yaml_file.write("---\n")
                for rule in self._rules:
                    yaml_str = self._yaml_transformer.transform(rule).getvalue()
                    yaml_file.write(yaml_str)
                    yaml_file.write("\n")
        except Exception as e:
            raise YAMLWriteError(f"Failed to write rules to YAML file: {e}")

    def write_default_trestle_rule_keys(self, filepath: pathlib.Path) -> None:
        """Write default TrestleRule keys to a YAML file."""
        try:
            test_rule = TrestleRule(
                name="example rule",
                description="example description",
                component=ComponentInfo(
                    name="example component",
                    type="service",
                    description="example description",
                ),
                profile=Profile(
                    description="example profile",
                    href="example href",
                    include_controls=[Control(id="example")],
                ),
            )
            self._yaml_transformer.write_to_file(test_rule, filepath)
        except Exception as e:
            raise YAMLWriteError(
                f"Failed to write empty TrestleRule keys to YAML file: {e}"
            )


class YAMLWriteError(Exception):
    """Exception raised for errors during YAML writing."""

    pass


class CSVReadError(Exception):
    """Exception raised for errors during CSV reading."""

    pass

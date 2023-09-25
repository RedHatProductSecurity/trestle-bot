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

"""YAML to CSV transformer for rule authoring."""
import csv
import pathlib
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from ruamel.yaml import YAML
from trestle.tasks.csv_to_oscal_cd import CsvColumn
from trestle.transforms.transformer_factory import TransformerBase


from trestlebot import const


@dataclass
class Parameter:
    name: str
    description: str
    alternative_values: dict
    default_value: str


@dataclass
class Profile:
    description: str
    href: str
    include_controls: List[str]


@dataclass
class TrestleRule:
    name: str
    description: str
    parameters: List[Parameter]
    profiles: List[Profile]


class RulesTransformer(TransformerBase):
    """Abstract interface for transformers for rules"""

    @abstractmethod
    def transform(self, blob: str) -> Dict[str, Any]:
        """Transform rule data."""


class CSVBuilder():

    def __init__(self) -> None:
        """Initialize."""
        self._csv_columns: CsvColumn = CsvColumn()
        self._rows: List[Dict[str, str]] = []

    def add_to_column(self, column: str, value: str) -> None:
        """Add a column to the CSV."""

    def add_row(self, row: Dict[str, str]) -> None:
        """Add a row to the CSV."""
        self._rows.append(row)

    def validate_row(self, row: Dict[str, str]) -> None:
        """Validate a row."""
        for key in self._csv_columns.get_required_column_names():
            if key not in row:
                raise RuntimeError(f'Row missing key: {key}')

    def write_to_file(self, filepath: pathlib.Path) -> None:
        """Write the CSV to file."""
        with open(filepath, mode='w', newline='') as csv_file:
            fieldnames: List[str] = []
            fieldnames.extend(self._csv_columns.get_required_column_names())
            fieldnames.extend(self._csv_columns.get_optional_column_names())

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in self._rows:
                writer.writerow(row)


class RulesYAMLToRulesCSVRowTransformer(RulesTransformer):
    """Interface for YAML to CSV transformer."""

    def __init__(self, csv_builder: CSVBuilder) -> None:
        """Initialize."""
        self._csv_builder = csv_builder
        super().__init__()

    def transform(self, blob: str) -> Dict[str, Any]:
        """Rules YAML data into a row of CSV."""
        trestle_rule: TrestleRule = self._ingest_yaml(blob)
        csv_data: Dict[str, Any] = {
            'Rule Name': trestle_rule.name,
            'Rule Description': trestle_rule.description,
            'Profile Count': len(trestle_rule.profiles),
            'Parameter Count': len(trestle_rule.parameters),
        }
        self._csv_builder.validate_row(csv_data)
        return csv_data

    @staticmethod
    def _ingest_yaml(blob: str) -> TrestleRule:
        """Ingest the YAML blob into a TrestleData object."""
        try:
            yaml = YAML(typ='safe')
            yaml_data: Dict[str, Any] = yaml.load(blob)
        except Exception as e:
            raise RuntimeError(e)

        rule_info_data = yaml_data[const.RULE_INFO_TAG]

        # Extract profile data and create a list of Profile instances
        profile_data = rule_info_data[const.PROFILES]
        profile_instances: List[Profile] = [Profile(**data) for data in profile_data]

        # Extract parameters from rule info and create a list of Parameter instances
        parameter_data = rule_info_data[const.PARAMETERS]
        parameter_instances: List[Parameter] = [Parameter(**data) for data in parameter_data]

        rule_info_instance: TrestleRule = TrestleRule(
            name=rule_info_data[const.NAME],
            description=rule_info_data[const.DESCRIPTION],
            parameters=parameter_instances,
            profiles=profile_instances
        )

        return rule_info_instance

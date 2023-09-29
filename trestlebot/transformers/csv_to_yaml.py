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
import json
import pathlib
from dataclasses import asdict, fields
from typing import Dict, List, Optional

import ruamel.yaml as yaml
import trestle.tasks.csv_to_oscal_cd as csv_to_oscal_cd

from trestlebot import const
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Parameter,
    Profile,
    TrestleRule,
)


class YAMLBuilder:
    def __init__(self) -> None:
        """Initialize."""
        self._rules: List[TrestleRule] = []

    def read_from_csv(self, filepath: pathlib.Path) -> None:
        """Read from a CSV file and populate self._rules."""
        try:
            with open(filepath, mode="r", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self._rules.append(self._csv_to_rule(row))
        except Exception as e:
            raise CSVReadError(f"Failed to read from CSV file: {e}")

    def _csv_to_rule(self, row: Dict[str, str]) -> TrestleRule:
        """Transform a CSV row to a TrestleRule object."""
        rule_info = self._extract_rule_info(row)
        profile = self._extract_profile(row)
        component_info = self._extract_component_info(row)
        parameter = self._extract_parameter(row)

        return TrestleRule(
            name=rule_info[const.NAME],
            description=rule_info[const.DESCRIPTION],
            component=component_info,
            parameter=parameter,
            profile=profile,
        )

    def _extract_rule_info(self, row: Dict[str, str]) -> Dict[str, str]:
        """Extract rule information from a CSV row."""
        return {
            "name": row.get(csv_to_oscal_cd.RULE_ID, ""),
            "description": row.get(csv_to_oscal_cd.RULE_DESCRIPTION, ""),
        }

    def _extract_profile(self, row: Dict[str, str]) -> Profile:
        """Extract profile information from a CSV row."""
        controls_list = row.get(csv_to_oscal_cd.CONTROL_ID_LIST, "").split(", ")
        return Profile(
            description=row.get(csv_to_oscal_cd.PROFILE_DESCRIPTION, ""),
            href=row.get(csv_to_oscal_cd.PROFILE_SOURCE, ""),
            include_controls=[
                Control(id=control_id.strip()) for control_id in controls_list
            ],
        )

    def _extract_parameter(self, row: Dict[str, str]) -> Optional[Parameter]:
        """Extract parameter information from a CSV row."""
        parameter_name = row.get(csv_to_oscal_cd.PARAMETER_ID, None)
        if parameter_name:
            return Parameter(
                name=parameter_name,
                description=row.get(csv_to_oscal_cd.PARAMETER_DESCRIPTION, ""),
                alternative_values=json.loads(
                    row.get(csv_to_oscal_cd.PARAMETER_VALUE_ALTERNATIVES, "{}")
                ),
                default_value=row.get(csv_to_oscal_cd.PARAMETER_VALUE_DEFAULT, ""),
            )
        return None

    def _extract_component_info(self, row: Dict[str, str]) -> ComponentInfo:
        """Extract component information from a CSV row."""
        return ComponentInfo(
            name=row.get(csv_to_oscal_cd.COMPONENT_TITLE, ""),
            type=row.get(csv_to_oscal_cd.COMPONENT_TYPE, ""),
            description=row.get(csv_to_oscal_cd.COMPONENT_DESCRIPTION, ""),
        )

    def write_to_yaml(self, filepath: pathlib.Path) -> None:
        """Write the rules to a YAML file."""
        try:
            with open(filepath, "w") as yaml_file:
                yaml.dump(
                    [asdict(rule) for rule in self._rules], yaml_file
                )  # Use Python's built-in asdict
        except Exception as e:
            raise YAMLWriteError(f"Failed to write rules to YAML file: {e}")

    def write_empty_trestle_rule_keys(self, filepath: pathlib.Path) -> None:
        """Write empty TrestleRule keys to a YAML file."""
        try:
            empty_dict = {f.name: "" for f in fields(TrestleRule)}
            with open(filepath, "w") as yaml_file:
                yaml.dump(empty_dict, yaml_file)
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

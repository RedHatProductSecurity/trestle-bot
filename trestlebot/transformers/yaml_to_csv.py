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
import logging
import pathlib
from typing import Any, Dict, List

from ruamel.yaml import YAML
from trestle.common.const import TRESTLE_GENERIC_NS
from trestle.tasks.csv_to_oscal_cd import (
    COMPONENT_DESCRIPTION,
    COMPONENT_TITLE,
    COMPONENT_TYPE,
    CONTROL_ID_LIST,
    NAMESPACE,
    PARAMETER_DESCRIPTION,
    PARAMETER_ID,
    PARAMETER_VALUE_ALTERNATIVES,
    PARAMETER_VALUE_DEFAULT,
    PROFILE_DESCRIPTION,
    PROFILE_SOURCE,
    RULE_DESCRIPTION,
    RULE_ID,
    CsvColumn,
)

from trestlebot import const
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Control,
    Parameter,
    Profile,
    RulesTransformer,
    RulesTransformerException,
    TrestleRule,
)


logger = logging.getLogger(__name__)


class RulesYAMLTransformer(RulesTransformer):
    """Interface for YAML transformer to Rules model."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()

    def transform(self, blob: str) -> TrestleRule:
        """Rules YAML data into a row of CSV."""
        trestle_rule: TrestleRule = self._ingest_yaml(blob)
        return trestle_rule

    @staticmethod
    def _ingest_yaml(blob: str) -> TrestleRule:
        """Ingest the YAML blob into a TrestleData object."""
        try:
            yaml = YAML(typ="safe")
            yaml_data: Dict[str, Any] = yaml.load(blob)

            rule_info_data = yaml_data[const.RULE_INFO_TAG]

            # Unpack profile data
            profile_data = rule_info_data[const.PROFILES]
            profile_instance: Profile = Profile(
                description=profile_data[const.DESCRIPTION],
                href=profile_data[const.HREF],
                include_controls=[
                    Control(**control)
                    for control in profile_data[const.INCLUDE_CONTROLS]
                ],
            )

            component_info_data = yaml_data[const.COMPONENT_INFO_TAG]
            component_info_instance: ComponentInfo = ComponentInfo(
                **component_info_data
            )

            rule_info_instance: TrestleRule = TrestleRule(
                name=rule_info_data[const.NAME],
                description=rule_info_data[const.DESCRIPTION],
                component=component_info_instance,
                parameter=None,
                profile=profile_instance,
            )

            if const.PARAMETERS in rule_info_data:
                parameter_data = rule_info_data[const.PARAMETERS]
                parameter_instance: Parameter = Parameter(
                    name=parameter_data[const.NAME],
                    description=parameter_data[const.DESCRIPTION],
                    alternative_values=parameter_data[const.ALTERNATIVE_VALUES],
                    default_value=parameter_data[const.DEFAULT_VALUE],
                )
                rule_info_instance.parameter = parameter_instance

        except KeyError as e:
            raise RulesTransformerException(f"Missing key in YAML file: {e}")
        except Exception as e:
            raise RuntimeError(e)

        return rule_info_instance


class CSVBuilder:
    def __init__(self) -> None:
        """Initialize."""
        self._csv_columns: CsvColumn = CsvColumn()
        self._rows: List[Dict[str, str]] = []

    @property
    def row_count(self) -> int:
        """Return the number of rows."""
        return len(self._rows)

    def add_row(self, rule: TrestleRule) -> None:
        """Add a row to the CSV."""
        row = self._rule_to_csv(rule)
        self.validate_row(row)
        self._rows.append(row)

    def validate_row(self, row: Dict[str, str]) -> None:
        """Validate a row."""
        for key in self._csv_columns.get_required_column_names():
            if key not in row:
                raise RuntimeError(f"Row missing key: {key}")

    def _rule_to_csv(self, rule: TrestleRule) -> Dict[str, str]:
        """Transform rules data to CSV."""
        rule_dict: Dict[str, str] = {
            RULE_ID: rule.name,
            RULE_DESCRIPTION: rule.description,
            NAMESPACE: TRESTLE_GENERIC_NS,
        }
        merged_dict = {
            **rule_dict,
            **self._add_profile(rule.profile),
            **self._add_component_info(rule.component),
        }
        if rule.parameter is not None:
            merged_dict.update(self._add_parameter(rule.parameter))
        return merged_dict

    def _add_profile(self, profile: Profile) -> Dict[str, str]:
        """Add a profile to the CSV Row."""
        controls_list: List[str] = [control.id for control in profile.include_controls]
        profile_dict: Dict[str, str] = {
            PROFILE_DESCRIPTION: profile.description,
            PROFILE_SOURCE: profile.href,
            CONTROL_ID_LIST: ", ".join(controls_list),
        }
        return profile_dict

    def _add_parameter(self, parameter: Parameter) -> Dict[str, str]:
        """Add a parameter to the CSV Row."""
        parameter_dict: Dict[str, str] = {
            PARAMETER_ID: parameter.name,
            PARAMETER_DESCRIPTION: parameter.description,
            PARAMETER_VALUE_ALTERNATIVES: f"{parameter.alternative_values}",
            PARAMETER_VALUE_DEFAULT: parameter.default_value,
        }
        return parameter_dict

    def _add_component_info(self, component_info: ComponentInfo) -> Dict[str, str]:
        """Add a component info to the CSV Row."""
        comp_dict: Dict[str, str] = {
            COMPONENT_TITLE: component_info.name,
            COMPONENT_DESCRIPTION: component_info.description,
            COMPONENT_TYPE: component_info.type,
        }
        return comp_dict

    def write_to_file(self, filepath: pathlib.Path) -> None:
        """Write the CSV to file."""
        logger.debug(f"Writing CSV to {filepath}")
        with open(filepath, mode="w", newline="") as csv_file:
            fieldnames: List[str] = []
            fieldnames.extend(self._csv_columns.get_required_column_names())
            fieldnames.extend(self._csv_columns.get_optional_column_names())

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in self._rows:
                writer.writerow(row)

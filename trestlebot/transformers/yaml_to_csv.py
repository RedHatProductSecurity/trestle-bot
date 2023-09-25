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
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from ruamel.yaml import YAML
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
class RuleInfo:
    name: str
    description: str
    parameters: List[Parameter]
    profiles: List[Profile]


@dataclass
class TrestleData:
    x_trestle_rule_info: RuleInfo


class RulesTransformer(TransformerBase):
    """Abstract interface for transformers for rules"""

    @abstractmethod
    def transform(self, blob: str) -> List[str]:
        """Transform the from OSCAL."""


class RulesYAMLToRulesCSVTransformer(TransformerBase):
    """Interface for YAML to CSV transformer."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()

    def transform(self, blob: str) -> List[str]:
        """Rules YAML data into a row of CSV."""
        return []

    @staticmethod
    def _ingest_yaml(blob: str) -> TrestleData:
        """Ingest the YAML blob into a TrestleData object."""
        try:
            yaml = YAML(typ='safe')
            yaml_data = yaml.load(blob)
        except Exception as e:
            raise RuntimeError(e)

        # Extract profile and rule info data
        rule_info_data = yaml_data[const.RULE_INFO_TAG]

        # Extract profile data and create a list of Profile instances
        profile_data = rule_info_data[const.PROFILES]
        profile_instances = [Profile(**data) for data in profile_data]

        # Extract parameters from rule info and create a list of Parameter instances
        parameter_data = rule_info_data[const.PARAMETERS]
        parameter_instances = [Parameter(**data) for data in parameter_data]

        # Create a RuleInfo instance that includes the list of Parameter instances
        rule_info_instance = RuleInfo(
            name=rule_info_data[const.NAME],
            description=rule_info_data[const.DESCRIPTION],
            parameters=parameter_instances,
            profiles=profile_instances
        )

        # Create an instance of the TrestleData data class with the RuleInfo
        trestle_data_instance = TrestleData(x_trestle_rule_info=rule_info_instance)

        return trestle_data_instance

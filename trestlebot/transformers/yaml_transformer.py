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

"""YAML transformer for rule authoring."""
import logging
import pathlib
from io import StringIO
from typing import Any, Dict

from pydantic import ValidationError
from ruamel.yaml import YAML

from trestlebot import const
from trestlebot.transformers.base_transformer import (
    FromRulesTransformer,
    RulesTransformerException,
    ToRulesTransformer,
)
from trestlebot.transformers.trestle_rule import (
    ComponentInfo,
    Parameter,
    Profile,
    TrestleRule,
)


logger = logging.getLogger(__name__)


class ToRulesYAMLTransformer(ToRulesTransformer):
    """Interface for YAML transformer to Rules model."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()

    def transform(self, blob: str) -> TrestleRule:
        """Transform YAML data into a TrestleRule object."""
        try:
            yaml = YAML(typ="safe")
            yaml_data: Dict[str, Any] = yaml.load(blob)

            rule_info_data = yaml_data[const.RULE_INFO_TAG]

            profile_data = rule_info_data[const.PROFILE]
            profile_info_instance: Profile = Profile.parse_obj(profile_data)

            component_info_data = yaml_data[const.COMPONENT_INFO_TAG]
            component_info_instance: ComponentInfo = ComponentInfo.parse_obj(
                component_info_data
            )

            rule_info_instance: TrestleRule = TrestleRule(
                name=rule_info_data[const.NAME],
                description=rule_info_data[const.DESCRIPTION],
                component=component_info_instance,
                parameter=None,
                profile=profile_info_instance,
            )

            if const.PARAMETER in rule_info_data:
                parameter_data = rule_info_data[const.PARAMETER]
                parameter_instance: Parameter = Parameter.parse_obj(parameter_data)
                rule_info_instance.parameter = parameter_instance

        except KeyError as e:
            raise RulesTransformerException(f"Missing key in YAML file: {e}")
        except ValidationError as e:
            raise RulesTransformerException(f"Invalid YAML file: {e}")

        return rule_info_instance


class FromRulesYAMLTransformer(FromRulesTransformer):
    """
    Interface for YAML transformer from Rules model.
    """

    def transform(self, rule: TrestleRule) -> StringIO:
        """
        Transform TrestleRule object into YAML data.

        Notes:
            Currently, this method is for simply transforming
            TrestleRule objects in memory into YAML data. The data structure
            is small so this should have minimal performance impact. This is done to
            comply with the contract of the RulesTransformer interface.
        """

        rule_info: Dict[str, Any] = self._to_rule_info(rule)
        yaml_obj = YAML()
        yaml_obj.default_flow_style = False
        yaml_stream = StringIO()
        yaml_obj.dump(rule_info, yaml_stream)

        return yaml_stream

    def write_to_file(self, rule: TrestleRule, file_path: pathlib.Path) -> None:
        """Write TrestleRule object to YAML file."""
        rule_info: Dict[str, Any] = self._to_rule_info(rule)
        yaml_obj = YAML()
        yaml_obj.default_flow_style = False
        yaml_obj.dump(rule_info, file_path)

    @staticmethod
    def _to_rule_info(rule: TrestleRule) -> Dict[str, Any]:
        """Convert YAML data to rule info."""
        rule_info: Dict[str, Any] = {
            const.RULE_INFO_TAG: {
                const.NAME: rule.name,
                const.DESCRIPTION: rule.description,
                const.PROFILE: rule.profile.dict(by_alias=True, exclude_unset=True),
            },
            const.COMPONENT_INFO_TAG: rule.component.dict(
                by_alias=True, exclude_unset=True
            ),
        }

        if rule.parameter is not None:
            rule_info[const.RULE_INFO_TAG][const.PARAMETER] = rule.parameter.dict(
                by_alias=True, exclude_unset=True
            )
        return rule_info

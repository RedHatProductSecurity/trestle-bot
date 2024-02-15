# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""YAML transformer for rule authoring."""
import logging
import pathlib
from io import StringIO
from typing import Any, Dict, Optional

from pydantic import ValidationError
from ruamel.yaml import YAML

from trestlebot import const
from trestlebot.transformers.base_transformer import (
    FromRulesTransformer,
    RulesTransformerException,
    ToRulesTransformer,
)
from trestlebot.transformers.trestle_rule import (
    Check,
    ComponentInfo,
    Parameter,
    Profile,
    TrestleRule,
)
from trestlebot.transformers.validations import ValidationHandler, ValidationOutcome


logger = logging.getLogger(__name__)


class ToRulesYAMLTransformer(ToRulesTransformer):
    """Interface for YAML transformer to Rules model."""

    def __init__(self, validator: Optional[ValidationHandler] = None) -> None:
        """Initialize."""
        self.validator: Optional[ValidationHandler] = validator
        super().__init__()

    def transform(self, blob: str) -> TrestleRule:
        """Transform YAML data into a TrestleRule object."""
        try:
            yaml = YAML(typ="safe")
            yaml_data: Dict[str, Any] = yaml.load(blob)

            logger.debug("Executing pre-validation on YAML data")
            if self.validator is not None:
                result = ValidationOutcome(errors=[], valid=True)
                self.validator.handle(yaml_data, result)
                if not result.valid:
                    raise RulesTransformerException(
                        f"Invalid YAML file: {result.errors}"
                    )

            rule_info_data = yaml_data[const.RULE_INFO_TAG]

            profile_info_instance = Profile.parse_obj(rule_info_data[const.PROFILE])

            component_info_instance = ComponentInfo.parse_obj(
                yaml_data[const.COMPONENT_INFO_TAG]
            )

            parameter_instance: Optional[Parameter] = None
            if const.PARAMETER in rule_info_data:
                parameter_instance = Parameter.parse_obj(
                    rule_info_data[const.PARAMETER]
                )

            check_instance: Optional[Check] = None
            if const.CHECK in rule_info_data:
                check_instance = Check.parse_obj(rule_info_data[const.CHECK])

            rule_info_instance: TrestleRule = TrestleRule(
                name=rule_info_data[const.NAME],
                description=rule_info_data[const.DESCRIPTION],
                component=component_info_instance,
                parameter=parameter_instance,
                profile=profile_info_instance,
                check=check_instance,
            )

        except KeyError as e:
            raise RulesTransformerException(f"Missing key in YAML file: {e}")
        except ValidationError as e:
            raise RulesTransformerException(f"Invalid YAML file: {e}")

        return rule_info_instance


class FromRulesYAMLTransformer(FromRulesTransformer):
    """
    Interface for YAML transformer from Rules model.
    """

    def transform(self, rule: TrestleRule) -> str:
        """
        Transform TrestleRule object into YAML data.

        Notes:
            Currently, this method is for simply transforming
            TrestleRule objects in memory into YAML data. The data structure
            is small so this should have minimal performance impact. This converts
            to a string for further processing. The write_to_file method
            is available for writing to a file directly.
        """

        rule_info: Dict[str, Any] = self._to_rule_info(rule)
        yaml_obj = YAML(typ="safe")
        yaml_obj.default_flow_style = False
        yaml_stream = StringIO()
        yaml_obj.dump(rule_info, yaml_stream)
        yaml_str = yaml_stream.getvalue()
        yaml_stream.close()

        return yaml_str

    def write_to_file(self, rule: TrestleRule, file_path: pathlib.Path) -> None:
        """Write TrestleRule object to YAML file."""
        rule_info: Dict[str, Any] = self._to_rule_info(rule)
        yaml_obj = YAML(typ="safe")
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
        if rule.check is not None:
            rule_info[const.RULE_INFO_TAG][const.CHECK] = rule.check.dict(
                by_alias=True, exclude_unset=True
            )
        return rule_info

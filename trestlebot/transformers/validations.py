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

"""
Trestle Validation for rule authoring.

This is meant to be extensible for future validations.
Base rule validation and utility functions are defined here.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

from trestlebot import const


logger = logging.getLogger(__name__)


class RuleValidationError(BaseModel):
    """RuleValidationError model."""

    field_name: str
    error_message: str


class ValidationOutcome(BaseModel):
    """ValidationOutcome model."""

    errors: List[RuleValidationError]
    valid: bool


class ValidationHandler:
    def __init__(  # type: ignore
        self, validate_fn: Callable[[Any, ValidationOutcome], None], next_handler=None
    ) -> None:
        self.validate_fn: Callable[[Any, ValidationOutcome], None] = validate_fn
        self.next_handler: Optional[ValidationHandler] = next_handler

    def handle(self, data: Any, result: ValidationOutcome) -> None:
        self.validate_fn(data, result)
        if self.next_handler:
            self.next_handler.handle(data, result)


def parameter_validation(data: Dict[str, Any], result: ValidationOutcome) -> None:
    """Parameter logic additions validation."""
    rule_info: Dict[str, Any] = data.get(const.RULE_INFO_TAG, {})
    parameter_data: Dict[str, Any] = rule_info.get(const.PARAMETER, {})

    if not parameter_data:
        logger.debug("No parameter data found")
        return  # No parameter data, nothing to validate

    default_value = parameter_data.get(const.DEFAULT_VALUE, "")
    alternative_values: Dict[str, Any] = parameter_data.get(
        const.ALTERNATIVE_VALUES, {}
    )

    if not default_value:
        add_validation_error(result, const.PARAMETER, "Default value is required")

    if not alternative_values:
        add_validation_error(result, const.PARAMETER, "Alternative values are required")

    default_value_alt = alternative_values.get("default", "")

    if not default_value_alt or default_value_alt != default_value:
        add_validation_error(
            result,
            const.PARAMETER,
            "Default value must be one of the alternative values",
        )


def add_validation_error(result: ValidationOutcome, field: str, error_msg: str) -> None:
    """Add a validation error to the result."""
    validation_error = RuleValidationError(field_name=field, error_message=error_msg)
    result.errors.append(validation_error)
    result.valid = False

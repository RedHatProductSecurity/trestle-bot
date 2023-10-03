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

"""Test for Validations."""
from typing import Any, Dict

from trestlebot.transformers.validations import (
    ValidationHandler,
    ValidationOutcome,
    parameter_validation,
)


def test_parameter_validation(valid_rule_data: Dict[str, Any]) -> None:
    """Test parameter validation with valid data."""
    result: ValidationOutcome = ValidationOutcome(errors=[], valid=True)
    parameter_validation(valid_rule_data, result)
    assert result.valid


def test_parameter_validation_with_error(
    invalid_param_rule_data: Dict[str, Any]
) -> None:
    """Test parameter validation with invalid parameter."""
    result: ValidationOutcome = ValidationOutcome(errors=[], valid=True)
    parameter_validation(invalid_param_rule_data, result)
    assert not result.valid
    assert len(result.errors) == 1
    assert (
        result.errors[0].error_message
        == "Default value must be one of the alternative values"
    )


def test_parameter_validation_with_handler(
    invalid_param_rule_data: Dict[str, Any]
) -> None:
    """Test parameter validation with handler."""
    result: ValidationOutcome = ValidationOutcome(errors=[], valid=True)
    handler = ValidationHandler(parameter_validation)
    handler.handle(invalid_param_rule_data, result)
    assert not result.valid
    assert len(result.errors) == 1
    assert (
        result.errors[0].error_message
        == "Default value must be one of the alternative values"
    )

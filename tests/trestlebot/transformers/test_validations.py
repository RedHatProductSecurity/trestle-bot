# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


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

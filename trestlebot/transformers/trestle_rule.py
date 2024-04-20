# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Trestle Rule class with pydantic."""


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from trestlebot import const


class Parameter(BaseModel):
    """Rule parameter model"""

    name: str
    description: str
    alternative_values: Dict[str, str] = Field(..., alias="alternative-values")
    default_value: str = Field(..., alias="default-value")

    class Config:
        allow_population_by_field_name = True

    @validator("default_value", pre=False)
    def check_default_value(cls, value: str, values: Dict[str, Any]) -> str:
        """Check if default value is in the alternative values."""
        alternative_values = values.get("alternative_values", {})
        if not alternative_values:
            raise ValueError("Alternative values must be provided")
        default_value_alt = alternative_values.get(const.DEFAULT_KEY, "")

        if not default_value_alt or default_value_alt != value:
            raise ValueError(
                f"Default value {value} must be in the alternative values {alternative_values}"
                f" under the key {const.DEFAULT_KEY}"
            )

        return value


class Control(BaseModel):
    """
    Catalog control for rule association

    Note: The control id or statement would be used here and
    trestle has additional validations for this field that won't
    be duplication in the rule model.
    """

    id: str


class Profile(BaseModel):
    """Profile source for rule association."""

    description: str
    href: str
    include_controls: List[Control] = Field(..., alias="include-controls")

    class Config:
        allow_population_by_field_name = True


class ComponentInfo(BaseModel):
    """Rule component model."""

    name: str
    type: str
    description: str


class Check(BaseModel):
    """Check model for rule validation."""

    name: str
    description: str

    class Config:
        allow_population_by_field_name = True


class TrestleRule(BaseModel):
    """Represents a Trestle rule."""

    name: str
    description: str
    component: ComponentInfo
    profile: Profile
    check: Optional[Check]
    parameter: Optional[Parameter]


def get_default_rule() -> TrestleRule:
    """Create a default rule for template purposes."""
    return TrestleRule(
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

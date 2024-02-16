# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Trestle Rule class with pydantic."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """Parameter dataclass."""

    name: str
    description: str
    alternative_values: Dict[str, Any] = Field(..., alias="alternative-values")
    default_value: str = Field(..., alias="default-value")

    class Config:
        allow_population_by_field_name = True


class Control(BaseModel):
    """Control dataclass."""

    id: str


class Profile(BaseModel):
    """Profile dataclass."""

    description: str
    href: str
    include_controls: List[Control] = Field(..., alias="include-controls")

    class Config:
        allow_population_by_field_name = True


class ComponentInfo(BaseModel):
    """ComponentInfo dataclass."""

    name: str
    type: str
    description: str


class Check(BaseModel):
    """Check dataclass."""

    name: str
    description: str

    class Config:
        allow_population_by_field_name = True


class TrestleRule(BaseModel):
    """TrestleRule dataclass."""

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

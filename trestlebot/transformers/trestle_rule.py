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


class TrestleRule(BaseModel):
    """TrestleRule dataclass."""

    name: str
    description: str
    component: ComponentInfo
    parameter: Optional[Parameter]
    profile: Profile


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

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

"""Trestle Rule Dataclass."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Parameter(BaseModel):
    """Parameter dataclass."""

    name: str
    description: str
    alternative_values: Dict[str, Any]
    default_value: str


class Control(BaseModel):
    """Control dataclass."""

    id: str


class Profile(BaseModel):
    """Profile dataclass."""

    description: str
    href: str
    include_controls: List[Control]


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

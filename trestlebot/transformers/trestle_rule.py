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

"""Trestle Rule Dataclass and base transformer."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from trestle.transforms.transformer_factory import TransformerBase


@dataclass
class Parameter:
    """Parameter dataclass."""

    name: str
    description: str
    alternative_values: dict
    default_value: str


@dataclass
class Control:
    """Control dataclass."""

    id: str


@dataclass
class Profile:
    """Profile dataclass."""

    description: str
    href: str
    include_controls: List[Control]


@dataclass
class ComponentInfo:
    """ComponentInfo dataclass."""

    name: str
    type: str
    description: str


@dataclass
class TrestleRule:
    """TrestleRule dataclass."""

    name: str
    description: str
    component: ComponentInfo
    parameter: Optional[Parameter]
    profile: Profile


class RulesTransformer(TransformerBase):
    """Abstract interface for transformers for rules"""

    @abstractmethod
    def transform(self, blob: str) -> TrestleRule:
        """Transform rule data."""


class RulesTransformerException(Exception):
    """An error during transformation of a rule"""

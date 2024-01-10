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

"""Base transformer for rules."""

# Evaluate if this should be contributed back to trestle

from abc import abstractmethod
from typing import Any

from trestle.transforms.transformer_factory import TransformerBase

from trestlebot.transformers.trestle_rule import TrestleRule


class ToRulesTransformer(TransformerBase):
    """Abstract interface for transforming to rule data."""

    @abstractmethod
    def transform(self, data: Any) -> TrestleRule:
        """Transform to rule data."""


class FromRulesTransformer(TransformerBase):
    """Abstract interface for transforming from rule data."""

    @abstractmethod
    def transform(self, rule: TrestleRule) -> Any:
        """Transform from rule data."""


class RulesTransformerException(Exception):
    """An error during transformation of a rule"""

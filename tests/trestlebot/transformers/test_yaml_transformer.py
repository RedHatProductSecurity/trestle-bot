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

"""Test for YAML Transformer."""

import pytest

from tests.testutils import YAML_TEST_DATA_PATH
from trestlebot.transformers.base_transformer import RulesTransformerException
from trestlebot.transformers.yaml_transformer import RulesYAMLTransformer


def test_rule_transformer() -> None:
    """Test rule transformer."""
    # load rule from path and close the file
    # get the file info as a string
    rule_path = YAML_TEST_DATA_PATH / "test_complete_rule.yaml"
    rule_file = open(rule_path, "r")
    rule_file_info = rule_file.read()
    rule_file.close()

    transformer = RulesYAMLTransformer()
    rule = transformer.transform_to_rule(rule_file_info)

    assert rule.name == "example_rule_1"
    assert rule.description == "My rule description for example rule 1"
    assert rule.component.name == "Component 1"
    assert rule.component.type == "service"
    assert rule.component.description == "Component 1 description"
    assert rule.parameter is not None
    assert rule.parameter.name == "prm_1"
    assert rule.parameter.description == "prm_1 description"
    assert rule.parameter.alternative_values == {
        "default": "5%",
        "5pc": "5%",
        "10pc": "10%",
        "15pc": "15%",
        "20pc": "20%",
    }
    assert rule.parameter.default_value == "5%"
    assert rule.profile.description == "Simple NIST Profile"
    assert rule.profile.href == "profiles/simplified_nist_profile/profile.json"


def test_rules_transform_with_incomplete_rule() -> None:
    """Test rules transform with incomplete rule."""
    # Generate test json string
    test_string = '{"test_json": "test"}'
    transformer = RulesYAMLTransformer()

    with pytest.raises(
        RulesTransformerException,
        match="Missing key in YAML file: 'x-trestle-rule-info'",
    ):
        transformer.transform_to_rule(test_string)


def test_rules_transform_with_invalid_rule() -> None:
    """Test rules transform with invalid rule."""
    # load rule from path and close the file
    # get the file info as a string
    rule_path = YAML_TEST_DATA_PATH / "test_invalid_rule.yaml"
    rule_file = open(rule_path, "r")
    rule_file_info = rule_file.read()
    rule_file.close()
    transformer = RulesYAMLTransformer()

    with pytest.raises(
        RulesTransformerException, match="Invalid YAML file: 1 validation error .*"
    ):
        transformer.transform_to_rule(rule_file_info)

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

"""Test for Trestle Bot rule transform task"""

import pathlib

import pytest
import trestle.oscal.component as osc_comp
from trestle.common.err import TrestleNotFoundError
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType
from trestle.tasks.csv_to_oscal_cd import RULE_DESCRIPTION, RULE_ID

from tests.testutils import setup_rules_view
from trestlebot.tasks.base_task import TaskException
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


test_comp = "test_comp"
test_rules_dir = "test_rules_dir"


def test_rule_transform_task(tmp_trestle_dir: str) -> None:
    """Test rule transform task."""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    setup_rules_view(trestle_root, test_comp, test_rules_dir)
    transformer = ToRulesYAMLTransformer()
    rule_transform_task = RuleTransformTask(
        tmp_trestle_dir, test_rules_dir, transformer
    )
    return_code = rule_transform_task.execute()
    assert return_code == 0

    # Check that the compdef model is unchanged
    orig_comp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_comp, osc_comp.ComponentDefinition, FileContentType.JSON
    )

    assert orig_comp is not None
    assert orig_comp.metadata.title == "Component definition for test_comp"
    assert orig_comp.components is not None
    assert len(orig_comp.components) == 2

    component = orig_comp.components[0]

    assert component.props is not None
    assert component.title == "Component 2"
    assert len(component.props) == 2
    assert component.props[0].name == RULE_ID
    assert component.props[0].value == "example_rule_2"
    assert component.props[1].name == RULE_DESCRIPTION
    assert component.props[1].value == "My rule description for example rule 2"

    component = orig_comp.components[1]

    assert component.props is not None
    assert component.title == "Component 1"
    assert len(component.props) == 5
    assert component.props[0].name == RULE_ID
    assert component.props[0].value == "example_rule_1"
    assert component.props[1].name == RULE_DESCRIPTION
    assert component.props[1].value == "My rule description for example rule 1"


def test_rule_transform_task_with_no_rules(tmp_trestle_dir: str) -> None:
    """Test rule transform task with no rules."""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    setup_rules_view(trestle_root, test_comp, test_rules_dir, skip_rules=True)
    transformer = ToRulesYAMLTransformer()
    rule_transform_task = RuleTransformTask(
        tmp_trestle_dir, test_rules_dir, transformer
    )

    with pytest.raises(
        TaskException, match="No rules found for component definition test_comp"
    ):
        rule_transform_task.execute()


def test_rule_transform_task_with_invalid_rule(tmp_trestle_dir: str) -> None:
    """Test rule transform task with invalid rule."""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    setup_rules_view(trestle_root, test_comp, test_rules_dir, incomplete_rule=True)
    transformer = ToRulesYAMLTransformer()
    rule_transform_task = RuleTransformTask(
        tmp_trestle_dir, test_rules_dir, transformer
    )

    with pytest.raises(
        TaskException, match="Failed to transform rule .*: Missing key in YAML file: .*"
    ):
        rule_transform_task.execute()


def test_rule_transform_task_with_skip(tmp_trestle_dir: str) -> None:
    """Test rule transform task with skip."""
    trestle_root = pathlib.Path(tmp_trestle_dir)
    setup_rules_view(trestle_root, test_comp, test_rules_dir)
    transformer = ToRulesYAMLTransformer()
    rule_transform_task = RuleTransformTask(
        tmp_trestle_dir, test_rules_dir, transformer, skip_model_list=[test_comp]
    )
    return_code = rule_transform_task.execute()
    assert return_code == 0

    # Check that the compdef model is not present
    with pytest.raises(TrestleNotFoundError):
        ModelUtils.load_model_for_class(
            trestle_root, test_comp, osc_comp.ComponentDefinition, FileContentType.JSON
        )

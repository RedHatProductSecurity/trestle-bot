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

"""Test for Trestle Bot Authored Compdef."""

import pathlib

import pytest
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.component import ComponentDefinition

from tests import testutils
from trestlebot.tasks.authored.base_authored import AuthoredObjectException
from trestlebot.tasks.authored.compdef import AuthoredComponentsDefinition


test_prof = "simplified_nist_profile"
test_comp = "test_comp"


def test_create_new_default(tmp_trestle_dir: str) -> None:
    """Test creating new default component definition"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_profile(trestle_root, test_prof, "")
    authored_comp = AuthoredComponentsDefinition(tmp_trestle_dir)

    authored_comp.create_new_default(test_prof, test_comp, "test", "My desc", "service")

    comp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_comp, ComponentDefinition, FileContentType.JSON
    )

    assert comp is not None

    assert comp.components is not None
    assert comp.components[0] is not None
    assert comp.components[0].control_implementations is not None

    assert (
        len(comp.components[0].control_implementations[0].implemented_requirements)
        == 12
    )


def test_create_new_default_existing(tmp_trestle_dir: str) -> None:
    """Test creating new default component in existing component definition"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_compdef(trestle_root, test_comp, "")
    authored_comp = AuthoredComponentsDefinition(tmp_trestle_dir)

    authored_comp.create_new_default(test_prof, test_comp, "test", "My desc", "service")

    comp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_comp, ComponentDefinition, FileContentType.JSON
    )

    assert comp is not None

    # Check new component
    assert comp.components is not None
    assert comp.components[1] is not None
    assert comp.components[1].control_implementations is not None

    assert (
        len(comp.components[1].control_implementations[0].implemented_requirements)
        == 12
    )

    # Check existing component
    assert comp.components[0] is not None
    assert comp.components[0].control_implementations is not None

    assert (
        len(comp.components[0].control_implementations[0].implemented_requirements) == 2
    )


def test_create_new_default_no_profile(tmp_trestle_dir: str) -> None:
    """Test creating new default component definition successfully"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_compdef(trestle_root, test_comp, "")

    authored_comp = AuthoredComponentsDefinition(tmp_trestle_dir)

    with pytest.raises(
        AuthoredObjectException, match="Profile fake does not exist in the workspace"
    ):
        authored_comp.create_new_default(
            "fake", test_comp, "test", "My desc", "service"
        )

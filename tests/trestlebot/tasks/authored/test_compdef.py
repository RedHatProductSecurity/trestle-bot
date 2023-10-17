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
import re

import pytest
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import profile as prof

from tests import testutils
from trestlebot.const import RULES_VIEW_DIR, YAML_EXTENSION
from trestlebot.tasks.authored.base_authored import AuthoredObjectException
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


test_prof = "simplified_nist_profile"
test_comp = "test_comp"


def test_create_new_default(tmp_trestle_dir: str) -> None:
    """Test creating new default component definition"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_profile(trestle_root, test_prof, "")
    authored_comp = AuthoredComponentDefinition(tmp_trestle_dir)

    authored_comp.create_new_default(test_prof, test_comp, "test", "My desc", "service")

    rules_view_dir = trestle_root / RULES_VIEW_DIR
    assert rules_view_dir.exists()

    compdef_dir = rules_view_dir / test_comp
    assert compdef_dir.exists()

    comp_dir = compdef_dir / "test"
    assert comp_dir.exists()

    yaml_files = list(comp_dir.glob(f"*{YAML_EXTENSION}"))
    assert len(yaml_files) == 12

    rule_file = next(
        (file for file in yaml_files if re.search(r"ac-5", file.stem)), None
    )
    assert rule_file is not None

    # Read one of the files and check the content
    rule_path = pathlib.Path(rule_file)
    rule_stream = rule_path.read_text()

    transformer = ToRulesYAMLTransformer()
    rule = transformer.transform(rule_stream)

    assert rule.name == "rule-ac-5"
    assert rule.description == "Rule for ac-5"
    assert rule.component.name == "test"
    assert rule.component.type == "service"
    assert rule.component.description == "My desc"
    assert rule.parameter is None
    assert rule.profile.description == (
        "NIST Special Publication 800-53 Revision 5 MODERATE IMPACT \
BASELINE"
    )
    assert (
        rule.profile.href == "trestle://profiles/simplified_nist_profile/profile.json"
    )
    assert rule.profile.include_controls is not None
    assert len(rule.profile.include_controls) == 1
    assert rule.profile.include_controls[0].id == "ac-5"


def test_create_new_default_with_filter(tmp_trestle_dir: str) -> None:
    """Test creating new default component definition with filter"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_profile(trestle_root, test_prof, "")
    authored_comp = AuthoredComponentDefinition(tmp_trestle_dir)

    profile_path = ModelUtils.get_model_path_for_name_and_class(
        trestle_root, test_prof, prof.Profile
    )

    catalog = ProfileResolver.get_resolved_profile_catalog(
        trestle_root, profile_path=profile_path
    )

    catalog_interface = CatalogInterface(catalog)
    catalog_interface.delete_control("ac-5")

    authored_comp.create_new_default(
        test_prof, test_comp, "test", "My desc", "service", catalog_interface
    )

    rules_view_dir = trestle_root / RULES_VIEW_DIR
    assert rules_view_dir.exists()

    compdef_dir = rules_view_dir / test_comp
    assert compdef_dir.exists()

    comp_dir = compdef_dir / "test"
    assert comp_dir.exists()

    # Verity that the number of rules YAML files has been reduced
    # from 12 to 11.
    yaml_files = list(comp_dir.glob(f"*{YAML_EXTENSION}"))
    assert len(yaml_files) == 11


def test_create_new_default_no_profile(tmp_trestle_dir: str) -> None:
    """Test creating new default component definition successfully"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_compdef(trestle_root, test_comp, "")

    authored_comp = AuthoredComponentDefinition(tmp_trestle_dir)

    with pytest.raises(
        AuthoredObjectException, match="Profile fake does not exist in the workspace"
    ):
        authored_comp.create_new_default(
            "fake", test_comp, "test", "My desc", "service"
        )

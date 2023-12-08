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

"""Test author types for Trestlebot"""

import os

import pytest

from tests import testutils
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectBase,
    AuthoredObjectException,
)
from trestlebot.tasks.authored.catalog import AuthoredCatalog
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.authored.ssp import AuthoredSSP


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_ssp_output = "test-ssp"
markdown_dir = "md_ssp"


def test_get_authored_catalog(tmp_trestle_dir: str) -> None:
    """Test get authored type for catalogs"""

    authored_object: AuthoredObjectBase = types.get_authored_object(
        types.AuthoredType.CATALOG.value, tmp_trestle_dir, ""
    )

    assert authored_object.get_trestle_root() == tmp_trestle_dir
    assert isinstance(authored_object, AuthoredCatalog)


def test_get_authored_profile(tmp_trestle_dir: str) -> None:
    """Test get authored type for catalogs"""

    authored_object: AuthoredObjectBase = types.get_authored_object(
        types.AuthoredType.PROFILE.value, tmp_trestle_dir, ""
    )

    assert authored_object.get_trestle_root() == tmp_trestle_dir
    assert isinstance(authored_object, AuthoredProfile)


def test_get_authored_compdef(tmp_trestle_dir: str) -> None:
    """Test get authored type for catalogs"""

    # Test with profile
    authored_object: AuthoredObjectBase = types.get_authored_object(
        types.AuthoredType.COMPDEF.value, tmp_trestle_dir, ""
    )

    assert authored_object.get_trestle_root() == tmp_trestle_dir
    assert isinstance(authored_object, AuthoredComponentDefinition)


def test_get_authored_ssp(tmp_trestle_dir: str) -> None:
    """Test get authored type for catalogs"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])

    with pytest.raises(
        FileNotFoundError,
    ):
        _ = types.get_authored_object(types.AuthoredType.SSP.value, tmp_trestle_dir, "")

    # Test with profile
    authored_object: AuthoredObjectBase = types.get_authored_object(
        types.AuthoredType.SSP.value, tmp_trestle_dir, ssp_index_path
    )

    assert authored_object.get_trestle_root() == tmp_trestle_dir
    assert isinstance(authored_object, AuthoredSSP)


def test_invalid_authored_type(tmp_trestle_dir: str) -> None:
    """Test triggering an error with an invalid type"""
    with pytest.raises(
        AuthoredObjectException,
        match="Invalid authored type fake",
    ):
        _ = types.get_authored_object("fake", tmp_trestle_dir, "")

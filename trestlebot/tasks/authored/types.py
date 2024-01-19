# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Trestle Bot authoring type information"""

from enum import Enum

from trestle.common import const

from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectBase,
    AuthoredObjectException,
)
from trestlebot.tasks.authored.catalog import AuthoredCatalog
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex


class AuthoredType(Enum):
    """Top-level OSCAL models that have authoring support"""

    CATALOG = "catalog"
    PROFILE = "profile"
    SSP = "ssp"
    COMPDEF = "compdef"


def get_authored_object(
    input_type: str, working_dir: str, ssp_index_path: str = ""
) -> AuthoredObjectBase:
    """Determine and configure author object context"""
    if input_type == AuthoredType.CATALOG.value:
        return AuthoredCatalog(working_dir)
    elif input_type == AuthoredType.PROFILE.value:
        return AuthoredProfile(working_dir)
    elif input_type == AuthoredType.COMPDEF.value:
        return AuthoredComponentDefinition(working_dir)
    elif input_type == AuthoredType.SSP.value:
        ssp_index: SSPIndex = SSPIndex(ssp_index_path)
        return AuthoredSSP(working_dir, ssp_index)
    else:
        raise AuthoredObjectException(f"Invalid authored type {input_type}")


def get_trestle_model_dir(authored_object: AuthoredObjectBase) -> str:
    """Determine directory for JSON content in trestle"""
    if isinstance(authored_object, AuthoredCatalog):
        return const.MODEL_DIR_CATALOG
    elif isinstance(authored_object, AuthoredProfile):
        return const.MODEL_DIR_PROFILE
    elif isinstance(authored_object, AuthoredComponentDefinition):
        return const.MODEL_DIR_COMPDEF
    elif isinstance(authored_object, AuthoredSSP):
        return const.MODEL_DIR_SSP
    else:
        raise AuthoredObjectException(
            f"Invalid authored object {type(authored_object)}"
        )

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Global constants"""

import trestle.common.const as trestle_const


# Common exit codes
SUCCESS_EXIT_CODE = 0
ERROR_EXIT_CODE = 1
INVALID_ARGS_EXIT_CODE = 2


# SSP Index Fields

PROFILE_KEY_NAME = "profile"
COMPDEF_KEY_NAME = "component_definitions"
LEVERAGED_SSP_KEY_NAME = "leveraged_ssp"

# Rule YAML Fields
RULE_INFO_TAG = trestle_const.TRESTLE_TAG + "rule-info"
NAME = "name"
DESCRIPTION = "description"
PARAMETER = "parameter"
PROFILE = "profile"
HREF = "href"
ALTERNATIVE_VALUES = "alternative-values"
DEFAULT_VALUE = "default-value"

COMPONENT_YAML = "component.yaml"
COMPONENT_INFO_TAG = trestle_const.TRESTLE_TAG + "component-info"

YAML_EXTENSION = ".yaml"

RULES_VIEW_DIR = "rules"
RULE_PREFIX = "rule-"

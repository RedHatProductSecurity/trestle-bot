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
YAML_HEADER_PATH_KEY_NAME = "yaml_header_path"

# Rule YAML Fields
RULE_INFO_TAG = trestle_const.TRESTLE_TAG + "rule-info"
NAME = "name"
DESCRIPTION = "description"
PARAMETER = "parameter"
CHECK = "check"
PROFILE = "profile"
HREF = "href"
ALTERNATIVE_VALUES = "alternative-values"
DEFAULT_KEY = "default"
DEFAULT_VALUE = "default-value"
TYPE = "type"
INCLUDE_CONTROLS = "include-controls"

COMPONENT_YAML = "component.yaml"
COMPONENT_INFO_TAG = trestle_const.TRESTLE_TAG + "component-info"

YAML_EXTENSION = ".yaml"

RULES_VIEW_DIR = "rules"
RULE_PREFIX = "rule-"


# GitHub Actions Outputs
COMMIT = "commit"
PR_NUMBER = "pr_number"
CHANGES = "changes"

# Git Provider Types
GITHUB = "github"
GITLAB = "gitlab"
GITHUB_SERVER_URL = "https://github.com"
GITHUB_WORKFLOWS_DIR = ".github/workflows"

# Trestlebot init constants
TRESTLEBOT_CONFIG_DIR = ".trestlebot"
TRESTLEBOT_KEEP_FILE = ".keep"

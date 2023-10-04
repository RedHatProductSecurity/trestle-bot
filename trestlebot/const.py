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

"""Global constants"""

import trestle.common.const as trestle_const


# Common exit codes
SUCCESS_EXIT_CODE = 0
ERROR_EXIT_CODE = 1


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

COMPONENT_YAML = "component.yaml"
COMPONENT_INFO_TAG = trestle_const.TRESTLE_TAG + "component-info"

YAML_EXTENSION = ".yaml"

RULES_VIEW_DIR = "rules"

#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot create compdef \
        --profile-name=\"${INPUT_TRESTLEBOT_PROFILE_NAME}\" \
        --compdef-name=\"${INPUT_TRESTLEBOT_COMPONENT_DEFINITION_NAME}\" \
        --component-title=\"${INPUT_TRESTLEBOT_COMPONENT_TITLE}\" \
        --component-description=\"${INPUT_TRESTLEBOT_COMPONENT_DESCRIPTION}\" \
        --component-definition-type=\"${INPUT_TRESTLEBOT_COMPONENT_TYPE}\" \
        --markdown-dir=\"${INPUT_TRESTLEBOT_MARKDOWN_DIR}\" \
        --commit-message=\"${INPUT_TRESTLEBOT_COMMIT_MESSAGE}\" \
        --filter-by-profile=\"${INPUT_TRESTLEBOT_FILTER_BY_PROFILE}\" \
        --pull-request-title=\"${INPUT_TRESTLEBOT_PULL_REQUEST_TITLE}\" \
        --branch=\"${INPUT_TRESTLEBOT_BRANCH}\" \
        --file-patterns=\"${INPUT_TRESTLEBOT_FILE_PATTERNS}\" \
        --committer-name=\"${INPUT_TRESTLEBOT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_TRESTLEBOT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_TRESTLEBOT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_TRESTLEBOT_COMMIT_AUTHOR_EMAIL}\" \
        --repo-path=\"${INPUT_TRESTLEBOT_REPO_PATH}\" \
        --target-branch=\"${INPUT_TRESTLEBOT_TARGET_BRANCH}\""

# Conditionally include flags
if [[ ${INPUT_TRESTLEBOT_VERBOSE} == true ]]; then
    command+=" --verbose"
fi

if [[ ${INPUT_TRESTLEBOT_DRY_RUN} == true ]]; then
    command+=" --dry-run"
fi

eval "${command}"

#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot create compdef \
        --profile-name=\"${INPUT_PROFILE_NAME}\" \
        --compdef-name=\"${INPUT_COMPONENT_DEFINITION_NAME}\" \
        --component-title=\"${INPUT_COMPONENT_TITLE}\" \
        --component-description=\"${INPUT_COMPONENT_DESCRIPTION}\" \
        --component-definition-type=\"${INPUT_COMPONENT_TYPE}\" \
        --markdown-dir=\"${INPUT_MARKDOWN_DIR}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
        --filter-by-profile=\"${INPUT_FILTER_BY_PROFILE}\" \
        --pull-request-title=\"${INPUT_PULL_REQUEST_TITLE}\" \
        --branch=\"${INPUT_BRANCH}\" \
        --file-patterns=\"${INPUT_FILE_PATTERNS}\" \
        --committer-name=\"${INPUT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_COMMIT_AUTHOR_EMAIL}\" \
        --repo-path=\"${INPUT_REPO_PATH}\" \
        --target-branch=\"${INPUT_TARGET_BRANCH}\""

# Conditionally include flags
if [[ ${INPUT_VERBOSE} == true ]]; then
    command+=" --verbose"
fi

if [[ ${INPUT_DRY_RUN} == true ]]; then
    command+=" --dry-run"
fi

eval "${command}"

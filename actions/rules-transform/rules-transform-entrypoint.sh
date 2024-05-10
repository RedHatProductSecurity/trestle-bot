#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot-rules-transform \
        --rules-view-path=\"${INPUT_RULES_VIEW_PATH}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
        --pull-request-title=\"${INPUT_PULL_REQUEST_TITLE}\" \
        --branch=\"${INPUT_BRANCH}\" \
        --file-patterns=\"${INPUT_FILE_PATTERN}\" \
        --committer-name=\"${INPUT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_COMMIT_AUTHOR_EMAIL}\" \
        --working-dir=\"${INPUT_REPOSITORY}\" \
        --target-branch=\"${INPUT_TARGET_BRANCH}\" \
        --skip-items=\"${INPUT_SKIP_ITEMS}\""

# Conditionally include flags
if [[ ${INPUT_VERBOSE} == true ]]; then
    command+=" --verbose"
fi

if [[ ${INPUT_DRY_RUN} == true ]]; then
    command+=" --dry-run"
fi

eval "${command}"
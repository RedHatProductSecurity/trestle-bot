#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Transform the input sources into a comma separated list
INPUT_TRESTLEBOT_SOURCES=$(echo "${INPUT_TRESTLEBOT_SOURCES}" | tr '\n' ' ' | tr -s ' ' | sed 's/ *$//' | tr ' ' ',')

# Initialize the command variable
command="trestlebot sync-upstreams \
        --sources=\"${INPUT_TRESTLEBOT_SOURCES}\" \
        --include-models=\"${INPUT_TRESTLEBOT_INCLUDE_MODELS}\" \
        --exclude-models=\"${INPUT_TRESTLEBOT_EXCLUDE_MODELS}\" \
        --commit-message=\"${INPUT_TRESTLEBOT_COMMIT_MESSAGE}\" \
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

if [[ ${INPUT_TRESTLEBOT_SKIP_VALIDATION} == true ]]; then
    command+=" --skip-validation"
fi

eval "${command}"

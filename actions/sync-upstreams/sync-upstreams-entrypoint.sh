#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Transform the input sources into a comma separated list
INPUT_SOURCES=$(echo "${INPUT_SOURCES}" | tr '\n' ' ' | tr -s ' ' | sed 's/ *$//' | tr ' ' ',')

# Initialize the command variable
command="trestlebot sync-upstreams \
        --sources=\"${INPUT_SOURCES}\" \
        --include-models=\"${INPUT_INCLUDE_MODELS}\" \
        --exclude-models=\"${INPUT_EXCLUDE_MODELS}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
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

if [[ ${INPUT_SKIP_VALIDATION} == true ]]; then
    command+=" --skip-validation"
fi

eval "${command}"

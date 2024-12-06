#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot autosync \
        --markdown-dir=\"${INPUT_TRESTLEBOT_MARKDOWN_DIR}\" \
        --oscal-model=\"${INPUT_TRESTLEBOT_OSCAL_MODEL}\" \
        --ssp-index-file=\"${INPUT_TRESTLEBOT_SSP_INDEX_FILE}\" \
        --commit-message=\"${INPUT_TRESTLEBOT_COMMIT_MESSAGE}\" \
        --pull-request-title=\"${INPUT_TRESTLEBOT_PULL_REQUEST_TITLE}\" \
        --branch=\"${INPUT_TRESTLEBOT_BRANCH}\" \
        --file-patterns=\"${INPUT_TRESTLEBOT_FILE_PATTERNS}\" \
        --committer-name=\"${INPUT_TRESTLEBOT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_TRESTLEBOT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_TRESTLEBOT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_TRESTLEBOT_COMMIT_AUTHOR_EMAIL}\" \
        --repo-path=\"${INPUT_TRESTLEBOT_REPO_PATH}\" \
        --target-branch=\"${INPUT_TRESTLEBOT_TARGET_BRANCH}\" \
        --skip-items=\"${INPUT_TRESTLEBOT_SKIP_ITEMS}\" \
        --version=\"${INPUT_TRESTLEBOT_VERSION}\""

# Conditionally include flags
if [[ ${INPUT_TRESTLEBOT_SKIP_ASSEMBLE} == true ]]; then
    command+=" --skip-assemble"
fi

if [[ ${INPUT_TRESTLEBOT_SKIP_REGENERATE} == true ]]; then
    command+=" --skip-regenerate"
fi

if [[ ${INPUT_TRESTLEBOT_DRY_RUN} == true ]]; then
    command+=" --dry-run"
fi

if [[ ${INPUT_TRESTLEBOT_VERBOSE} == true ]]; then
    command+=" --verbose"
fi

eval "${command}"

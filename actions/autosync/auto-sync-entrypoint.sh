#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot autosync \
        --markdown-dir=\"${INPUT_MARKDOWN_DIR}\" \
        --oscal-model=\"${INPUT_OSCAL_MODEL}\" \
        --ssp-index-file=\"${INPUT_SSP_INDEX_FILE}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
        --branch=\"${INPUT_BRANCH}\" \
        --file-patterns=\"${INPUT_FILE_PATTERNS}\" \
        --committer-name=\"${INPUT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_COMMIT_AUTHOR_EMAIL}\" \
        --repo-path=\"${INPUT_REPO_PATH}\" \
        --target-branch=\"${INPUT_TARGET_BRANCH}\" \
        --skip-items=\"${INPUT_SKIP_ITEMS}\" \
        --version=\"${INPUT_VERSION}\"
        --config=\"${INPUT_CONFIG}\""

# Conditionally include flags
if [[ ${INPUT_SKIP_ASSEMBLE} == true ]]; then
    command+=" --skip-assemble"
fi

if [[ ${INPUT_SKIP_REGENERATE} == true ]]; then
    command+=" --skip-regenerate"
fi

if [[ ${INPUT_DRY_RUN} == true ]]; then
    command+=" --dry-run"
fi

if [[ ${INPUT_DEBUG} == true ]]; then
    command+=" --debug"
fi

eval "${command}"

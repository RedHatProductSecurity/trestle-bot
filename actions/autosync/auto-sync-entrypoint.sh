#!/bin/bash

set -eu

# shellcheck disable=SC1091
source /common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot-autosync \
        --markdown-path=\"${INPUT_MARKDOWN_PATH}\" \
        --oscal-model=\"${INPUT_OSCAL_MODEL}\" \
        --ssp-index-path=\"${INPUT_SSP_INDEX_PATH}\" \
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
if [[ ${INPUT_SKIP_ASSEMBLE} == true ]]; then
    command+=" --skip-assemble"
fi

if [[ ${INPUT_SKIP_REGENERATE} == true ]]; then
    command+=" --skip-regenerate"
fi

if [[ ${INPUT_CHECK_ONLY} == true ]]; then
    command+=" --check-only"
fi

if [[ ${INPUT_VERBOSE} == true ]]; then
    command+=" --verbose"
fi

# Only set the token value when is a target branch so pull requests can be created
if [[ -n ${INPUT_TARGET_BRANCH} ]]; then
  if [[ -z ${GITHUB_TOKEN} ]]; then
    echo "Set the GITHUB_TOKEN env variable."
    exit 1
  fi

  command+=" --with-token - <<<\"${GITHUB_TOKEN}\""
fi

execute_command "${command}"
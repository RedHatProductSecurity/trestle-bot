#!/bin/bash

set -eu

# shellcheck disable=SC1091
source ./common.sh

set_git_safe_directory

# Initialize the command variable
command="trestlebot-create-cd \
        --profile-name=\"${INPUT_PROFILE_NAME}\" \
        --compdef-name=\"${INPUT_COMPONENT_DEFINITION_NAME}\" \
        --component-title=\"${INPUT_COMPONENT_TITLE}\" \
        --component-description=\"${INPUT_COMPONENT_DESCRIPTION}\" \
        --component-definition-type=\"${INPUT_COMPONENT_TYPE}\" \
        --markdown-path=\"${INPUT_MARKDOWN_PATH}\" \
        --commit-message=\"${INPUT_COMMIT_MESSAGE}\" \
        --filter-by-profile=\"${INPUT_FILTER_BY_PROFILE}\" \
        --pull-request-title=\"${INPUT_PULL_REQUEST_TITLE}\" \
        --branch=\"${INPUT_BRANCH}\" \
        --file-patterns=\"${INPUT_FILE_PATTERN}\" \
        --committer-name=\"${INPUT_COMMIT_USER_NAME}\" \
        --committer-email=\"${INPUT_COMMIT_USER_EMAIL}\" \
        --author-name=\"${INPUT_COMMIT_AUTHOR_NAME}\" \
        --author-email=\"${INPUT_COMMIT_AUTHOR_EMAIL}\" \
        --working-dir=\"${INPUT_REPOSITORY}\" \
        --target-branch=\"${INPUT_TARGET_BRANCH}\""

# Conditionally include flags
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
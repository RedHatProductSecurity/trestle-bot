#!/bin/bash

set -eu

commit=$(python3.8 -m trestlebot \
        --markdown-path="${INPUT_MARKDOWN_PATH}" \
        --assemble-model="${INPUT_ASSEMBLE_MODEL}" \
        --ssp-index-path="${INPUT_SSP_INDEX_PATH}" \
        --commit-message="${INPUT_COMMIT_MESSAGE}" \
        --branch="${INPUT_BRANCH}" \
        --patterns="${INPUT_FILE_PATTERN}" \
        --committer-name="${INPUT_COMMIT_USER_NAME}" \
        --committer-email="${INPUT_COMMIT_USER_EMAIL}" \
        --author-name="${INPUT_COMMIT_AUTHOR_NAME}" \
        --author-email="${INPUT_COMMIT_AUTHOR_EMAIL}" \
        --working-dir="${INPUT_WORKING_DIR}")

if [ -n "$commit" ]; then
    echo "changes=true" >> "$GITHUB_OUTPUT"
    echo "commit=$commit" >> "$GITHUB_OUTPUT"
else
    echo "changes=false" >> "$GITHUB_OUTPUT"
fi

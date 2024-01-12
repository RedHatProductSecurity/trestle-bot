# shellcheck disable=SC2148

# common.sh
# This file is sourced by other scripts and contains common functions

# Manage newest git versions (related to CVE https://github.blog/2022-04-12-git-security-vulnerability-announced/)
#
function set_git_safe_directory() {
    if [[ -z "${GITHUB_WORKSPACE+x}" ]]; then
    echo "Setting git safe.directory default: /github/workspace ..."
    git config --global --add safe.directory /github/workspace
    else
    echo "Setting git safe.directory GITHUB_WORKSPACE: $GITHUB_WORKSPACE ..."
    git config --global --add safe.directory "$GITHUB_WORKSPACE"
    fi

    if [[ -z "${INPUT_REPOSITORY+x}" ]]; then
        echo "Skipping setting working directory as safe directory"
    else
    echo "Setting git safe.directory default: $INPUT_REPOSITORY ..."
    git config --global --add safe.directory "$INPUT_REPOSITORY"
    fi
}

# Execute the command and set the output variables for GitHub Actions
function execute_command() {
    local command=$1
    exec 3>&1
    output=$(eval "$command" > >(tee /dev/fd/3) 2>&1)

    commit=$(echo "$output" | grep "Commit Hash:" | sed 's/.*: //')

    if [ -n "$commit" ]; then
        echo "changes=true" >> "$GITHUB_OUTPUT"
        echo "commit=$commit" >> "$GITHUB_OUTPUT"
    else
        echo "changes=false" >> "$GITHUB_OUTPUT"
    fi

    pr_number=$(echo "$output" | grep "Pull Request Number:" | sed 's/.*: //')

    if [ -n "$pr_number" ]; then 
    echo "pr_number=$pr_number" >> "$GITHUB_OUTPUT"
    fi
}

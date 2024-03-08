# shellcheck disable=SC2148

# common.sh
# This file is sourced by other scripts and contains common functions

# Manage newest git versions (related to CVE https://github.blog/2022-04-12-git-security-vulnerability-announced/)
#
function set_git_safe_directory() {
    if [[ -z "${GITHUB_WORKSPACE}" ]]; then
        echo "GITHUB_WORKSPACE is not set. Exiting..."
        exit 1
    else
        echo "Setting git safe.directory GITHUB_WORKSPACE: $GITHUB_WORKSPACE ..."
        git config --global --add safe.directory "$GITHUB_WORKSPACE"
    fi
}

# Execute the command and set the output variables for GitHub Actions
function execute_command() {
    local command=$1
    exec 3>&1
    output=$(eval "$command" > >(tee /dev/fd/3) 2>&1)

    changes=$(echo "$output" | grep "Changes:" | sed 's/.*: //')
    commit=$(echo "$output" | grep "Commit Hash:" | sed 's/.*: //')

    if [[ -n "$commit" ]]; then
        echo "changes=true" >> "$GITHUB_OUTPUT"
        echo "commit=$commit" >> "$GITHUB_OUTPUT"
        
        pr_number=$(echo "$output" | grep "Pull Request Number:" | sed 's/.*: //')

        if [[ -n "$pr_number" ]]; then 
            echo "pr_number=$pr_number" >> "$GITHUB_OUTPUT"
        fi
    elif [[ -n "$changes" ]]; then
        echo "changes=true" >> "$GITHUB_OUTPUT"
    else
        echo "changes=false" >> "$GITHUB_OUTPUT"
    fi
}

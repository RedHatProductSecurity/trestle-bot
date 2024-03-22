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


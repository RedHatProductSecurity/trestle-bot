# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""GitHub related functions for the Trestle Bot."""

import os
import re
from typing import Optional, Tuple

import github3
from github3.exceptions import AuthenticationFailed
from github3.repos.repo import Repository

from trestlebot.provider import GitProvider, GitProviderException


class GitHub(GitProvider):
    """Create GitHub object to interact with the GitHub API"""

    def __init__(self, access_token: str):
        """
        Initialize GitHub Object

        Args:
            access_token: Access token to make authenticated API requests.
        """
        session: github3.GitHub = github3.GitHub()
        session.login(token=access_token)

        self._session = session
        self.pattern = r"^(?:https?://)?github\.com/([^/]+)/([^/.]+)"

    def parse_repository(self, repo_url: str) -> Tuple[str, str]:
        """
        Parse repository url

        Args:
            repo_url: Valid url for a GitHub repo

        Returns:
            Owner and repo name in a tuple, respectively
        """

        match = re.match(self.pattern, repo_url)

        if not match:
            raise GitProviderException(f"{repo_url} is an invalid GitHub repo URL")

        owner = match.group(1)
        repo = match.group(2)
        return (owner, repo)

    def create_pull_request(
        self,
        ns: str,
        repo_name: str,
        base_branch: str,
        head_branch: str,
        title: str,
        body: str,
    ) -> int:
        """
        Create a pull request in the repository

        Args:
            ns: Namespace or owner of the repository
            repo_name: Name of the repository
            base_branch: Branch that changes need to be merged into
            head_branch: Branch with changes
            title: Text for the title of the pull_request
            body: Text for the body of the pull request

        Returns:
            Pull request number
        """
        try:
            repository: Optional[Repository] = self._session.repository(
                owner=ns, repository=repo_name
            )
            if repository is None:
                raise GitProviderException(
                    f"Repository for {ns}/{repo_name} cannot be None"
                )

            pull_request = repository.create_pull(
                title=title, body=body, base=base_branch, head=head_branch
            )

            if pull_request:
                return pull_request.number
            else:
                raise GitProviderException(
                    (
                        f"Failed to create pull request in {ns}/{repo_name}"
                        f"for {head_branch} to {base_branch}"
                    )
                )
        except AuthenticationFailed as e:
            raise GitProviderException(
                f"Authentication error during pull request creation in {ns}/{repo_name}: {e}"
            )


# GitHub ref:
# https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
def is_github_actions() -> bool:
    """Determine in the environment is GitHub Actions"""
    var_value = os.getenv("GITHUB_ACTIONS")
    if var_value and var_value.lower() in ["true", "1"]:
        return True
    return False

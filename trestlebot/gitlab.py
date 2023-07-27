#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""GitLab related functions for the Trestle Bot."""

import re
from typing import Tuple

import gitlab

from trestlebot.provider import GitProvider, GitProviderException


class GitLab(GitProvider):
    def __init__(self, api_token: str, server_url: str = "https://gitlab.com"):
        """Create GitLab object to interact with the GitLab API"""

        self._gitlab_client = gitlab.Gitlab(server_url, private_token=api_token)

        stripped_url = re.sub(r"^(https?://)?", "", server_url)
        self.pattern = r"^(?:https?://)?{0}/([^/]+)/([^/.]+)".format(
            re.escape(stripped_url)
        )

    def parse_repository(self, repo_url: str) -> Tuple[str, str]:
        """
        Parse repository url

        Args:
            repo_url: Valid url for a GitLab repo

        Returns:
            Owner and project name in a tuple, respectively
        """
        match = re.match(self.pattern, repo_url)

        if not match:
            raise GitProviderException(f"{repo_url} is an invalid repo URL")

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
        Create a pull (merge request in the GitLab) request in the repository

        Args:
            ns: Namespace or owner of the repository
            repo_name: Name of the repository
            base_branch: Branch that changes need to be merged into
            head_branch: Branch with changes
            title: Text for the title of the pull_request
            body: Text for the body of the pull request

        Returns:
            Pull/Merge request number
        """

        try:
            project = self._gitlab_client.projects.get(f"{ns}/{repo_name}")
            merge_request = project.mergerequests.create(
                {
                    "source_branch": head_branch,
                    "target_branch": base_branch,
                    "title": title,
                    "description": body,
                }
            )

            return merge_request.id

        except gitlab.exceptions.GitlabCreateError as e:
            raise GitProviderException(
                f"Failed to create merge request in {ns}/{repo_name}: {e}"
            )
        except gitlab.exceptions.GitlabAuthenticationError as e:
            raise GitProviderException(
                f"Authentication error during merge request creation in {ns}/{repo_name}: {e}"
            )

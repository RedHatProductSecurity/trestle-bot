# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

import logging
from typing import Optional

from trestlebot import const
from trestlebot.github import GitHub, is_github_actions
from trestlebot.gitlab import GitLab, get_gitlab_root_url, is_gitlab_ci
from trestlebot.provider import GitProvider


logger = logging.getLogger(__name__)


class GitProviderFactory:
    """Factory class for creating Git provider objects"""

    @staticmethod
    def provider_factory(
        access_token: str, type: str = "", server_url: str = ""
    ) -> GitProvider:
        """
        Factory class for creating Git provider objects

        Args:
            access_token: Access token for the Git provider
            type: Type of Git provider. Supported values are "github" or "gitlab"
            server_url: URL of the Git provider server

        Returns:
            a GitProvider object

        Notes:
            If type is not provided, the method will attempt to detect the Git provider from the
            environment.

        Raises:
            ValueError: If the server URL is provided for GitHub provider
            RuntimeError: If the Git provider cannot be detected
        """

        git_provider: Optional[GitProvider] = None

        if type == const.GITHUB:
            logger.debug("Creating GitHub provider")
            if server_url and server_url != "https://github.com":
                raise ValueError("GitHub provider does not support custom server URLs")
            git_provider = GitHub(access_token=access_token)
        elif type == const.GITLAB:
            logger.debug("Creating GitLab provider")
            if not server_url:
                git_provider = GitLab(api_token=access_token)
            else:
                git_provider = GitLab(api_token=access_token, server_url=server_url)
        else:
            logger.debug(
                "No type or server_url provided."
                "Detecting Git provider from environment."
            )
            git_provider = GitProviderFactory._detect_from_environment(access_token)

        if git_provider is None:
            raise RuntimeError(
                "Could not detect Git provider from environment or inputs"
            )

        return git_provider

    @staticmethod
    def _detect_from_environment(access_token: str) -> Optional[GitProvider]:
        """Detect the Git provider from the environment"""
        git_provider: Optional[GitProvider] = None
        if is_github_actions():
            logging.debug("Detected GitHub Actions environment")
            git_provider = GitHub(access_token=access_token)
        elif is_gitlab_ci():
            logging.debug("Detected GitLab CI environment")
            server_api_url = get_gitlab_root_url()
            git_provider = GitLab(api_token=access_token, server_url=server_api_url)
        return git_provider

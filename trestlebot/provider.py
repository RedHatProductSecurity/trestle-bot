# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Base Git Provider class for the Trestle Bot."""

from abc import ABC, abstractmethod
from typing import Tuple


class GitProviderException(Exception):
    """An error when interacting with a Git provider"""


class GitProvider(ABC):
    """
    Abstract base class for Git provider types
    """

    @abstractmethod
    def parse_repository(self, repository_url: str) -> Tuple[str, str]:
        """Parse repository information into namespace and repo, respectively"""

    @abstractmethod
    def create_pull_request(
        self,
        ns: str,
        repo_name: str,
        base_branch: str,
        head_branch: str,
        title: str,
        body: str,
    ) -> int:
        """Create a pull request for a specified branch and return the request number"""

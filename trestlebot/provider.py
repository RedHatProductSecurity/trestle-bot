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

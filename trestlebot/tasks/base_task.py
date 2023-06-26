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

"""Trestle Bot base task for extendable bot pre-tasks"""

from abc import ABC, abstractmethod


# TODO: Incorporate a configuration file for model specific tasks


class TaskException(Exception):
    """An error during task execution"""


class TaskBase(ABC):
    """
    Abstract base class for tasks with a work directory.
    """

    def __init__(self, working_dir: str) -> None:
        """
        Initialize base task.

        Args:
            working_dir: Working directory to complete operations in.
        """
        self._working_dir = working_dir

    def get_working_dir(self) -> str:
        """Return the working directory"""
        return self._working_dir

    @abstractmethod
    def execute(self) -> int:
        """Execute the task and return the exit code"""

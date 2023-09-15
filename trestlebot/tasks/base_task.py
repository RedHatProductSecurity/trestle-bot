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

import fnmatch
import pathlib
from abc import ABC, abstractmethod
from typing import Iterable, List

from trestle.common import const
from trestle.common.file_utils import is_hidden


class TaskException(Exception):
    """An error during task execution"""


class TaskBase(ABC):
    """
    Abstract base class for tasks with a work directory.
    """

    def __init__(self, working_dir: str, skip_list: List[str]) -> None:
        """
        Initialize base task.

        Args:
            working_dir: Working directory to complete operations in.
            skip_list: List of glob pattern to be skipped during processing.
        """
        self._working_dir = working_dir
        self._skip_model_list = skip_list
        self._skip_model_list.append(const.TRESTLE_KEEP_FILE)

    def get_working_dir(self) -> str:
        """Return the working directory"""
        return self._working_dir

    def iterate_models(self, directory_path: pathlib.Path) -> Iterable[pathlib.Path]:
        """Iterate over the models in the working directory"""
        filtered_paths = list(
            filter(
                lambda p: not self._is_skipped(p.name)
                and (not is_hidden(p) or p.is_dir()),
                pathlib.Path.iterdir(directory_path),
            )
        )

        return filtered_paths.__iter__()

    def _is_skipped(self, model_name: str) -> bool:
        """Return True if the model is in the skip list"""
        return any(
            fnmatch.fnmatch(model_name, pattern) for pattern in self._skip_model_list
        )

    @abstractmethod
    def execute(self) -> int:
        """Execute the task and return the exit code"""

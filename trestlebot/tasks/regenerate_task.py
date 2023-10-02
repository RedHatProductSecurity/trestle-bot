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

"""Trestle Bot Regenerate Tasks"""

import os
import pathlib
from typing import List

from trestlebot import const
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)
from trestlebot.tasks.base_task import TaskBase, TaskException


class RegenerateTask(TaskBase):
    """
    Regenerate Trestle Markdown from OSCAL JSON content changes
    """

    def __init__(
        self,
        working_dir: str,
        authored_model: str,
        markdown_dir: str,
        ssp_index_path: str = "",
        skip_model_list: List[str] = [],
    ) -> None:
        """
        Initialize regenerate task.

        Args:
            working_dir: Working directory to complete operations in
            authored_model: String representation of model type
            markdown_dir: Location of directory to write Markdown in
            ssp_index_path: Path of ssp index JSON in the workspace
            skip_model_list: List of model names to be skipped during processing
        """

        self._authored_model = authored_model
        self._markdown_dir = markdown_dir
        self._ssp_index_path = ssp_index_path
        super().__init__(working_dir, skip_model_list)

    def execute(self) -> int:
        """Execute task"""
        return self._regenerate()

    def _regenerate(self) -> int:
        """
        Regenerate all objects in model JSON directory

        Returns:
         0 on success, raises an exception if not successful
        """
        authored_object: AuthorObjectBase = types.get_authored_object(
            self._authored_model, self.working_dir, self._ssp_index_path
        )

        model_dir = types.get_trestle_model_dir(self._authored_model)

        search_path = os.path.join(self.working_dir, model_dir)
        for model in self.iterate_models(pathlib.Path(search_path)):
            model_base_name = os.path.basename(model)
            model_path = os.path.join(model_dir, model_base_name)

            try:
                authored_object.regenerate(
                    model_path=model_path, markdown_path=self._markdown_dir
                )
            except AuthoredObjectException as e:
                raise TaskException(f"Regenerate task failed for model {model}: {e}")

        return const.SUCCESS_EXIT_CODE

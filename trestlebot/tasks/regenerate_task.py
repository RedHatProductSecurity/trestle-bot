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
from typing import Optional

from trestlebot import const
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectBase,
    AuthoredObjectException,
)
from trestlebot.tasks.base_task import ModelFilter, TaskBase, TaskException


class RegenerateTask(TaskBase):
    """
    Regenerate Trestle Markdown from OSCAL JSON content changes
    """

    def __init__(
        self,
        authored_object: AuthoredObjectBase,
        markdown_dir: str,
        model_filter: Optional[ModelFilter] = None,
    ) -> None:
        """
        Initialize regenerate task.

        Args:
            authored_object: Object that can regenerate Markdown content from JSON
            markdown_dir: Location of directory to write Markdown in
            model_filter: Optional filter to apply to the task to include or exclude models
            from processing.
        """

        self._authored_object = authored_object
        self._markdown_dir = markdown_dir
        working_dir = self._authored_object.get_trestle_root()
        super().__init__(working_dir, model_filter)

    def execute(self) -> int:
        """Execute task"""
        return self._regenerate()

    def _regenerate(self) -> int:
        """
        Regenerate all objects in model JSON directory

        Returns:
         0 on success, raises an exception if not successful
        """
        model_dir = types.get_trestle_model_dir(self._authored_object)

        search_path = os.path.join(self.working_dir, model_dir)
        for model in self.iterate_models(pathlib.Path(search_path)):
            model_base_name = os.path.basename(model)
            model_path = os.path.join(model_dir, model_base_name)

            try:
                self._authored_object.regenerate(
                    model_path=model_path, markdown_path=self._markdown_dir
                )
            except AuthoredObjectException as e:
                raise TaskException(f"Regenerate task failed for model {model}: {e}")

        return const.SUCCESS_EXIT_CODE

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

"""Trestle Bot Assembly Tasks"""

import os

from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import (
    AuthoredObjectException,
    AuthorObjectBase,
)
from trestlebot.tasks.authored.catalog import AuthoredCatalog
from trestlebot.tasks.authored.compdef import AuthoredComponentsDefinition
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex
from trestlebot.tasks.base_task import TaskBase, TaskException


class AssembleTask(TaskBase):
    """
    Assemble Markdown into OSCAL content
    """

    def __init__(
        self,
        working_dir: str,
        authored_model: types.AuthoredType,
        markdown_dir: str,
        ssp_index_path: str = "",
    ) -> None:
        """
        Initialize assemble task.

        Args:
            working_dir: Working directory to complete operations in.
            authored_model: Model type .
            markdown_dir: Working directory to complete operations in.
            ssp_index_path:

        """

        self._authored_model = authored_model
        self._markdown_dir = markdown_dir
        self._ssp_index_path = ssp_index_path
        super().__init__(working_dir)

    def execute(self) -> int:
        """Execute task"""
        return self._assemble()

    def _assemble(self) -> int:
        """Assemble all objects in markdown directory"""
        authored_object: AuthorObjectBase = self._get_authored_object()
        search_path = os.path.join(self._working_dir, self._markdown_dir)
        for model in os.listdir(search_path):
            # Construct model path from markdown. AuthoredObject already
            # have the working dir data.
            model_path = os.path.join(self._markdown_dir, model)
            try:
                authored_object.assemble(model_path=model_path)
            except AuthoredObjectException as e:
                raise TaskException(f"Assemble task failed for model {model_path}: {e}")
        return 0

    def _get_authored_object(self) -> AuthorObjectBase:
        """Determine and configure author object context"""
        if self._authored_model is types.AuthoredType.CATALOG:  # noqa: E721
            return AuthoredCatalog(self._working_dir)
        elif self._authored_model is types.AuthoredType.PROFILE:  # noqa: E721
            return AuthoredProfile(self._working_dir)
        elif self._authored_model is types.AuthoredType.COMPDEF:  # noqa: E721
            return AuthoredComponentsDefinition(self._working_dir)
        elif self._authored_model is types.AuthoredType.SSP:  # noqa: E721
            ssp_index: SSPIndex = SSPIndex(self._ssp_index_path)
            return AuthoredSSP(self._working_dir, ssp_index)
        else:
            raise TaskException(f"Invalid authored type {self._authored_model}")

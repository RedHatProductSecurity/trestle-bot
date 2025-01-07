# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Trestle Bot Rule Transform Tasks"""

from typing import Optional

import trestlebot.const as const
from trestlebot.tasks.base_task import ModelFilter, TaskBase


class SyncCacContentTask(TaskBase):
    """
    Transform rules into OSCAL content.
    """

    def __init__(
        self,
        working_dir: str,
        model_filter: Optional[ModelFilter] = None,
    ) -> None:
        """
        Initialize transform task.

        Args:
            working_dir: Working directory to complete operations in
            model_filter: Optional filter to apply to the task to include or exclude models
            from processing.
        """
        super().__init__(working_dir, model_filter)

    def execute(self) -> int:
        """Execute task"""
        return const.SUCCESS_EXIT_CODE

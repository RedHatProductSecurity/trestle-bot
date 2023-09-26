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

import pathlib
from typing import List

import trestlebot.const as const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.yaml_to_csv import (
    CSVBuilder,
    RulesYAMLToRulesCSVRowTransformer,
)


class RuleTransformTask(TaskBase):
    """
    Transform Rules Markdown into OSCAL content
    """

    def __init__(
        self,
        working_dir: str,
        rules_dir: str,
        skip_model_list: List[str] = [],
    ) -> None:
        """
        Initialize transform task.

        Args:
            working_dir: Working directory to complete operations in
            rules_dir: Location of directory to read Rules YAML from
            skip_model_list: List of rule names to be skipped during processing
        """

        self._rules_dir = rules_dir
        super().__init__(working_dir, skip_model_list)

    def execute(self) -> int:
        """Execute task"""
        return self._transform()

    def _transform(self) -> int:
        """
        Transform rule objects into OSCAL

        Returns:
         0 on success, raises an exception if not successful
        """
        working_path: pathlib.Path = pathlib.Path(self.working_dir)
        search_path: pathlib.Path = working_path.joinpath(self._rules_dir)

        csv_builder: CSVBuilder = CSVBuilder()
        for rule in self.iterate_models(search_path):
            # Load the rule into memory as a stream to process
            rule_stream = rule.read_text()

            transformer = RulesYAMLToRulesCSVRowTransformer(csv_builder)
            row = transformer.transform(rule_stream)
            csv_builder.add_row(row)

        # Write the CSV to disk
        csv_path: pathlib.Path = working_path.joinpath(const.TRESTLE_RULES_CSV)
        csv_builder.write_to_file(csv_path)

        # Build config for CSV to OSCAL task
        # Execute task

        return const.SUCCESS_EXIT_CODE

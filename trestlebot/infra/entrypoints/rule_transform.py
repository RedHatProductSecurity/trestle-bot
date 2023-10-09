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

"""Entrypoint for component definition rules transformation."""

import argparse
import logging
from typing import List

import trestle.common.log as log

from trestlebot.entrypoint_base import EntrypointBase
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.validations import ValidationHandler, parameter_validation
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


logger = logging.getLogger(__name__)


class RulesTransformEntrypoint(EntrypointBase):
    """Entrypoint for the rules transformation operation."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        # Setup base arguments
        super().__init__(parser)
        self.setup_rules_transformation_arguments()

    def setup_rules_transformation_arguments(self) -> None:
        """Setup arguments for the rule transformer entrypoint."""
        self.parser.add_argument(
            "--rules-view-path",
            required=True,
            type=str,
            help="Path to Trestle markdown files",
        )
        self.parser.add_argument(
            "--skip-items",
            type=str,
            required=False,
            help="Comma-separated list of glob patterns of the chosen model type to skip when running \
                tasks",
        )

    def run(self, args: argparse.Namespace) -> None:
        """Run the rule transform entrypoint."""

        log.set_log_level_from_args(args=args)

        validation_handler: ValidationHandler = ValidationHandler(parameter_validation)
        transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer(validation_handler)

        rule_transform_task: RuleTransformTask = RuleTransformTask(
            args.working_dir,
            args.rules_view_path,
            transformer,
            args.skip_items,
        )
        pre_tasks: List[TaskBase] = [rule_transform_task]

        super().run_base(args, pre_tasks)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Rules transformation entrypoint for trestle."
    )
    rules_transform = RulesTransformEntrypoint(parser=parser)

    args = parser.parse_args()

    rules_transform.run(args)


if __name__ == "__main__":
    main()

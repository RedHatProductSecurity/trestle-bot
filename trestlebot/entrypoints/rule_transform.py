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

from trestlebot.entrypoints.entrypoint_base import EntrypointBase, comma_sep_to_list
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.base_task import ModelFilter, TaskBase
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
            help="Path to top-level rules-view directory",
        )
        self.parser.add_argument(
            "--skip-items",
            type=str,
            required=False,
            help="Comma-separated list of glob patterns for directories to skip when running \
                tasks",
        )

    def run(self, args: argparse.Namespace) -> None:
        """Run the rule transform entrypoint."""

        set_log_level_from_args(args)

        # Configure the YAML Transformer for the task
        validation_handler: ValidationHandler = ValidationHandler(parameter_validation)
        transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer(validation_handler)

        filter: ModelFilter = ModelFilter(
            skip_patterns=comma_sep_to_list(args.skip_items),
            include_patterns=["."],
        )

        rule_transform_task: RuleTransformTask = RuleTransformTask(
            working_dir=args.working_dir,
            rules_view_dir=args.rules_view_path,
            rule_transformer=transformer,
            filter=filter,
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

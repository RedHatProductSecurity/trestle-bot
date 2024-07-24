# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Entrypoint for component definition rules transformation."""

import argparse
import logging
import sys
import traceback
from typing import List

from trestlebot.const import RULES_VIEW_DIR, SUCCESS_EXIT_CODE
from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    comma_sep_to_list,
    handle_exception,
)
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask
from trestlebot.tasks.rule_transform_task import RuleTransformTask
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
            "--markdown-path",
            required=True,
            type=str,
            help="Path to create markdown files in.",
        )
        self.parser.add_argument(
            "--rules-view-path",
            required=False,
            type=str,
            help="Path to top-level rules-view directory",
            default=RULES_VIEW_DIR,
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
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)

            # Allow any model to be skipped from the args, by default include all
            model_filter: ModelFilter = ModelFilter(
                skip_patterns=comma_sep_to_list(args.skip_items),
                include_patterns=["*"],
            )

            transformer = ToRulesYAMLTransformer()
            rule_transform_task: RuleTransformTask = RuleTransformTask(
                working_dir=args.working_dir,
                rules_view_dir=args.rules_view_path,
                rule_transformer=transformer,
                model_filter=model_filter,
            )
            regenerate_task: RegenerateTask = RegenerateTask(
                markdown_dir=args.markdown_path,
                authored_object=AuthoredComponentDefinition(args.working_dir),
                model_filter=model_filter,
            )

            pre_tasks: List[TaskBase] = [rule_transform_task, regenerate_task]

            super().run_base(args, pre_tasks)
        except Exception as e:
            traceback_str = traceback.format_exc()
            exit_code = handle_exception(e, traceback_str)

        sys.exit(exit_code)


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

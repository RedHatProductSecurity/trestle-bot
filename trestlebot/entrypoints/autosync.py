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


"""
This module parses the default entrypoint for the Trestle Bot.

This is the default entrypoint for the Trestle Bot which performs
autosync operations using compliance-trestle.
"""

import argparse
import logging
import sys
from typing import List

from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    EntrypointInvalidArgException,
    comma_sep_to_list,
    handle_exception,
)
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask


logger = logging.getLogger(__name__)


class AutoSyncEntrypoint(EntrypointBase):
    """Entrypoint for the autosync operation."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        # Setup base arguments
        super().__init__(parser)
        self.setup_autosync_arguments()

    def setup_autosync_arguments(self) -> None:
        """Setup arguments for the autosync entrypoint."""
        self.parser.add_argument(
            "--markdown-path",
            required=True,
            type=str,
            help="Path to Trestle markdown files",
        )
        self.parser.add_argument(
            "--oscal-model",
            required=True,
            type=str,
            choices=["catalog", "profile", "compdef", "ssp"],
            help="OSCAL model type to run tasks on.",
        )
        self.parser.add_argument(
            "--skip-items",
            type=str,
            required=False,
            help="Comma-separated list of glob patterns of the chosen model type to skip when running \
                tasks",
        )
        self.parser.add_argument(
            "--skip-assemble",
            required=False,
            action="store_true",
            help="Skip assembly task. Defaults to false",
        )
        self.parser.add_argument(
            "--skip-regenerate",
            required=False,
            action="store_true",
            help="Skip regenerate task. Defaults to false",
        )
        self.parser.add_argument(
            "--ssp-index-path",
            required=False,
            type=str,
            default="ssp-index.json",
            help="Path to ssp index file",
        )

    def validate_args(self, args: argparse.Namespace) -> None:
        """Validate the arguments for the autosync entrypoint."""
        authored_list: List[str] = [model.value for model in types.AuthoredType]
        if args.oscal_model not in authored_list:
            raise EntrypointInvalidArgException(
                "--oscal-model",
                f"Value {args.oscal_model} is not valid."
                f"Please use one of {authored_list}",
            )

        if not args.markdown_path:
            raise EntrypointInvalidArgException(
                "--markdown-path", "Markdown path must be set."
            )

        if (
            args.oscal_model == types.AuthoredType.SSP.value
            and args.ssp_index_path == ""
        ):
            raise EntrypointInvalidArgException(
                "--ssp-index-path",
                "Must set ssp index path when using SSP as oscal model.",
            )

    def run(self, args: argparse.Namespace) -> None:
        """Run the autosync entrypoint."""
        exit_code = 0
        try:
            set_log_level_from_args(args)
            self.validate_args(args)

            pre_tasks: List[TaskBase] = []
            # Allow any model to be skipped from the args, by default include all
            model_filter: ModelFilter = ModelFilter(
                skip_patterns=comma_sep_to_list(args.skip_items),
                include_patterns=["*"],
            )

            authored_object: AuthoredObjectBase = types.get_authored_object(
                args.oscal_model, args.working_dir, args.ssp_index_path
            )

            # Assuming an edit has occurred assemble would be run before regenerate.
            # Adding this to the list first
            if not args.skip_assemble:
                assemble_task = AssembleTask(
                    authored_object=authored_object,
                    markdown_dir=args.markdown_path,
                    model_filter=model_filter,
                )
                pre_tasks.append(assemble_task)
            else:
                logger.info("Assemble task skipped.")

            if not args.skip_regenerate:
                regenerate_task = RegenerateTask(
                    authored_object=authored_object,
                    markdown_dir=args.markdown_path,
                    model_filter=model_filter,
                )
                pre_tasks.append(regenerate_task)
            else:
                logger.info("Regeneration task skipped.")

            super().run_base(args, pre_tasks)
        except Exception as e:
            exit_code = handle_exception(e)

        sys.exit(exit_code)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Workflow automation bot for compliance-trestle"
    )

    auto_sync = AutoSyncEntrypoint(parser=parser)

    args = parser.parse_args()

    auto_sync.run(args)


if __name__ == "__main__":
    main()

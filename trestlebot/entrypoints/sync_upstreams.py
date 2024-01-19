#!/usr/bin/python

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""
Entrypoint for synchronizing content from upstreams git sources.

Note: This currently does not following imports of the synced OSCAL content.
"""

import argparse
import logging
import sys
from typing import List

from trestlebot.const import SUCCESS_EXIT_CODE
from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    EntrypointInvalidArgException,
    comma_sep_to_list,
    handle_exception,
)
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.sync_upstreams_task import SyncUpstreamsTask


logger = logging.getLogger(__name__)


class SyncUpstreamsEntrypoint(EntrypointBase):
    """Entrypoint for the sync upstreams operation."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        # Setup base arguments
        super().__init__(parser)
        self.setup_sync_upstreams_arguments()

    def setup_sync_upstreams_arguments(self) -> None:
        """Setup arguments for the sync upstreams entrypoint."""
        self.parser.add_argument(
            "--sources",
            type=str,
            required=True,
            help="Comma-separated list of upstream git sources to fetch from. Each source is a string \
                of the form <repo_url>@<ref> where ref is a git ref such as a tag or branch.",
        )
        self.parser.add_argument(
            "--include-model-names",
            type=str,
            required=False,
            help="Comma-separated list of glob patterns for model names to include when running \
                tasks (e.g. --include-models=component_x,profile_y*)",
        )
        self.parser.add_argument(
            "--exclude-model-names",
            type=str,
            required=False,
            help="Comma-separated list of glob patterns for model names to exclude when running \
                tasks (e.g. --exclude-models=component_x,profile_y*)",
        )
        self.parser.add_argument(
            "--skip-validation",
            action="store_true",
            help="Skip validation of the models when they are copied",
        )

    def run(self, args: argparse.Namespace) -> None:
        """Run the sync upstreams entrypoint."""
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)
            if not args.sources:
                raise EntrypointInvalidArgException(
                    "--sources", "Must set at least one source to sync from."
                )

            # Assume that if exclude_model_names is not set, then
            # skip nothing and if include_model_names is not set, then include all.
            include_model_list: List[str] = ["*"]
            if args.include_model_names:
                include_model_list = comma_sep_to_list(args.include_model_names)
            model_filter: ModelFilter = ModelFilter(
                skip_patterns=comma_sep_to_list(args.exclude_model_names),
                include_patterns=include_model_list,
            )

            validate: bool = not args.skip_validation

            sync_upstreams_task: TaskBase = SyncUpstreamsTask(
                working_dir=args.working_dir,
                git_sources=comma_sep_to_list(args.sources),
                model_filter=model_filter,
                validate=validate,
            )
            pre_tasks: List[TaskBase] = [sync_upstreams_task]

            super().run_base(args, pre_tasks)
        except Exception as e:
            exit_code = handle_exception(e)

        sys.exit(exit_code)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Sync content from upstreams git sources."
    )
    sync_upstreams = SyncUpstreamsEntrypoint(parser=parser)

    args = parser.parse_args()

    sync_upstreams.run(args)


if __name__ == "__main__":
    main()

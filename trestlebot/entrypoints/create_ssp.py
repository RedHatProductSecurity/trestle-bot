#!/usr/bin/python

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""
Entrypoint for system security plan bootstrapping.

This will create and initial SSP with markdown, an SSP index, and a SSP JSON file.
"""

import argparse
import logging
import pathlib
import sys
from typing import List

from trestlebot.const import SUCCESS_EXIT_CODE
from trestlebot.entrypoints.entrypoint_base import (
    EntrypointBase,
    comma_sep_to_list,
    handle_exception,
)
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex
from trestlebot.tasks.base_task import ModelFilter, TaskBase


logger = logging.getLogger(__name__)


class CreateSSPEntrypoint(EntrypointBase):
    """Entrypoint for ssp bootstrapping."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        super().__init__(parser)
        self.setup_create_ssp_arguments()

    def setup_create_ssp_arguments(self) -> None:
        """Setup specific arguments for this entrypoint."""
        self.parser.add_argument(
            "--ssp-name", required=True, type=str, help="Name of SSP to create."
        )
        self.parser.add_argument(
            "--profile-name",
            required=True,
            help="Name of profile in the trestle workspace to include in the SSP.",
        )
        self.parser.add_argument(
            "--compdefs",
            required=True,
            type=str,
            help="Comma-separated list of component definitions to include in the SSP",
        )
        self.parser.add_argument(
            "--leveraged-ssp",
            required=False,
            type=str,
            help="Provider SSP to leverage for the new SSP.",
        )
        self.parser.add_argument(
            "--markdown-path",
            required=True,
            type=str,
            help="Path to create markdown files in.",
        )
        self.parser.add_argument(
            "--yaml-header-path",
            required=False,
            type=str,
            help="Optionally set a path to a YAML file for custom SSP Markdown YAML headers.",
        )
        self.parser.add_argument(
            "--version",
            required=False,
            type=str,
            help="Optionally set the SSP version.",
        )
        self.parser.add_argument(
            "--ssp-index-path",
            required=False,
            type=str,
            default="ssp-index.json",
            help="Optionally set the path to the SSP index file.",
        )

    def run(self, args: argparse.Namespace) -> None:
        """Run the entrypoint."""
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)

            # If the ssp index file does not exist, create it.
            ssp_index_path = pathlib.Path(args.ssp_index_path)
            if not ssp_index_path.exists():
                # Create a parent directory
                ssp_index_path.parent.mkdir(parents=True, exist_ok=True)

            ssp_index: SSPIndex = SSPIndex(args.ssp_index_path)
            authored_ssp: AuthoredSSP = AuthoredSSP(args.working_dir, ssp_index)

            comps: List[str] = comma_sep_to_list(args.compdefs)
            authored_ssp.create_new_default(
                ssp_name=args.ssp_name,
                profile_name=args.profile_name,
                compdefs=comps,
                markdown_path=args.markdown_path,
                leveraged_ssp=args.leveraged_ssp,
                yaml_header=args.yaml_header_path,
            )

            # The starting point for SSPs is the markdown, so assemble into JSON.
            model_filter: ModelFilter = ModelFilter([], [args.ssp_name])
            assemble_task: AssembleTask = AssembleTask(
                authored_object=authored_ssp,
                markdown_dir=args.markdown_path,
                version=args.version,
                model_filter=model_filter,
            )
            pre_tasks: List[TaskBase] = [assemble_task]

            super().run_base(args, pre_tasks)
        except Exception as e:
            exit_code = handle_exception(e)

        sys.exit(exit_code)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Create new system security plan for editing."
    )
    create_ssp = CreateSSPEntrypoint(parser=parser)

    args = parser.parse_args()
    create_ssp.run(args)


if __name__ == "__main__":
    main()

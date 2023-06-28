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


"""This module parses CLI arguments for the Trestle Bot."""

import argparse
import logging
import sys
from typing import List

from trestlebot import bot
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.base_task import TaskBase


logging.basicConfig(
    format="%(levelname)s - %(message)s", stream=sys.stdout, level=logging.INFO
)


def _parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automation git actions for compliance-trestle"
    )
    parser.add_argument(
        "--branch",
        type=str,
        required=True,
        help="Branch name to push changes to",
    )
    parser.add_argument(
        "--markdown-path",
        required=True,
        type=str,
        help="Path to Trestle markdown files",
    )
    parser.add_argument(
        "--assemble-model",
        required=True,
        type=str,
        help="OSCAL Model type to assemble. Values can be catalog, profile, compdef, or ssp",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=False,
        default=".",
        help="Working directory wit git repository",
    )
    parser.add_argument(
        "--commit-message",
        type=str,
        required=False,
        default="chore: automatic updates",
        help="Commit message for automated updates",
    )
    parser.add_argument(
        "--committer-name",
        type=str,
        required=True,
        help="Name of committer",
    )
    parser.add_argument(
        "--committer-email",
        type=str,
        required=True,
        help="Email for committer",
    )
    parser.add_argument(
        "--author-name",
        required=False,
        type=str,
        default="",
        help="Name for commit author if differs from committer",
    )
    parser.add_argument(
        "--author-email",
        required=False,
        type=str,
        default="",
        help="Email for commit author if differs from committer",
    )
    parser.add_argument(
        "--ssp-index-path",
        required=False,
        type=str,
        default="ssp-index.txt",
        help="Path to ssp index file",
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        type=str,
        required=True,
        help="List of file patterns to include in repository updates",
    )
    return parser.parse_args()


def handle_exception(
    exception: Exception, msg: str = "Exception occurred during execution"
) -> int:
    """Log the exception and return the exit code"""
    logging.exception(msg + f": {exception}")

    return 1


def run() -> None:
    """Trestle Bot entry point function."""
    args = _parse_cli_arguments()
    pre_tasks: List[TaskBase] = []

    # Pre-process flags
    if args.assemble_model:
        assembled_type: types.AuthoredType
        try:
            assembled_type = types.check_authored_type(args.assemble_model)
        except ValueError:
            logging.error(
                f"Invalid value {args.assemble_model} for assemble model. \
                    Please use catalog, profile, compdef, or ssp."
            )
            sys.exit(1)

        if not args.markdown_path:
            logging.error("Must set markdown path with assemble model.")
            sys.exit(1)

        if args.assemble_model == "ssp" and args.ssp_index_path == "":
            logging.error("Must set ssp_index_path when using SSP as assemble model.")
            sys.exit(1)

        assemble_task = AssembleTask(
            args.working_dir,
            assembled_type,
            args.markdown_path,
            args.ssp_index_path,
        )
        pre_tasks.append(assemble_task)

    exit_code: int = 0

    # Assume it is a successful run, if the bot
    # throws an exception update the exit code accordingly
    try:
        commit_sha = bot.run(
            working_dir=args.working_dir,
            branch=args.branch,
            commit_name=args.committer_name,
            commit_email=args.committer_email,
            commit_message=args.commit_message,
            author_name=args.author_name,
            author_email=args.author_email,
            pre_tasks=pre_tasks,
            patterns=args.patterns,
        )

        # Print the full commit sha
        print(f' Commit Hash: {commit_sha}')

    except Exception as e:
        exit_code = handle_exception(e)

    sys.exit(exit_code)

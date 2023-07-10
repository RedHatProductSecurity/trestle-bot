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
import os
import sys
from typing import List, Optional

from trestlebot import bot, log
from trestlebot.github import GitHub
from trestlebot.provider import GitProvider
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask


logger = logging.getLogger("trestle")


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
        "--oscal-model",
        required=True,
        type=str,
        help="OSCAL model type to run tasks on. Values can be catalog, profile, compdef, or ssp",
    )
    parser.add_argument(
        "--file-patterns",
        required=True,
        type=str,
        help="Comma-separated list of file patterns to be used with `git add` in repository updates",
    )
    parser.add_argument(
        "--skip-items",
        type=str,
        required=False,
        help="Comma-separated list of items of the chosen model type to skip when running tasks",
    )
    parser.add_argument(
        "--skip-assemble",
        required=False,
        action="store_true",
        help="Skip assembly task. Defaults to false",
    )
    parser.add_argument(
        "--skip-regenerate",
        required=False,
        action="store_true",
        help="Skip regenerate task. Defaults to false.",
    )
    parser.add_argument(
        "--check-only",
        required=False,
        action="store_true",
        help="Runs tasks and exits with an error if there is a diff",
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
        help="Name for commit author if differs from committer",
    )
    parser.add_argument(
        "--author-email",
        required=False,
        type=str,
        help="Email for commit author if differs from committer",
    )
    parser.add_argument(
        "--ssp-index-path",
        required=False,
        type=str,
        default="ssp-index.json",
        help="Path to ssp index file",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        action="store_true",
        help="Run in verbose mode",
    )
    parser.add_argument(
        "--target-branch",
        type=str,
        required=False,
        help="Target branch or base branch to create a pull request against. \
        No pull request is created if unset",
    )
    parser.add_argument(
        "--with-token",
        nargs="?",
        type=argparse.FileType("r"),
        required=False,
        default=sys.stdin,
        help="Read token from standard input for authenticated requests with \
        Git provider (e.g. create pull requests)",
    )
    return parser.parse_args()


def handle_exception(
    exception: Exception, msg: str = "Exception occurred during execution"
) -> int:
    """Log the exception and return the exit code"""
    logger.error(msg + f": {exception}", exc_info=True)

    return 1


def run() -> None:
    """Trestle Bot entry point function."""

    args = _parse_cli_arguments()
    log.set_log_level_from_args(args=args)

    pre_tasks: List[TaskBase] = []
    git_provider: Optional[GitProvider] = None

    authored_list: List[str] = [model.value for model in types.AuthoredType]

    # Pre-process flags

    if args.oscal_model:
        if args.oscal_model not in authored_list:
            logger.error(
                f"Invalid value {args.oscal_model} for oscal model. "
                f"Please use catalog, profile, compdef, or ssp."
            )
            sys.exit(1)

        if not args.markdown_path:
            logger.error("Must set markdown path with oscal model.")
            sys.exit(1)

        if args.oscal_model == "ssp" and args.ssp_index_path == "":
            logger.error("Must set ssp_index_path when using SSP as oscal model.")
            sys.exit(1)

        # Assuming an edit has occurred assemble would be run before regenerate.
        # Adding this to the list first
        if not args.skip_assemble:
            assemble_task = AssembleTask(
                args.working_dir,
                args.oscal_model,
                args.markdown_path,
                args.ssp_index_path,
                comma_sep_to_list(args.skip_items),
            )
            pre_tasks.append(assemble_task)
        else:
            logger.info("Assemble task skipped")

        if not args.skip_regenerate:
            regenerate_task = RegenerateTask(
                args.working_dir,
                args.oscal_model,
                args.markdown_path,
                args.ssp_index_path,
                comma_sep_to_list(args.skip_items),
            )
            pre_tasks.append(regenerate_task)
        else:
            logger.info("Regeneration task skipped")

    if args.target_branch:
        if not is_github_actions():
            logger.error(
                "target-branch flag is set with an unsupported git provider. "
                "If testing locally with the GitHub API, set "
                "the GITHUB_ACTIONS environment variable to true."
            )
            sys.exit(1)

        if not args.with_token:
            logger.error("with-token value cannot be empty")
            sys.exit(1)

        git_provider = GitHub(access_token=args.with_token.read().strip())

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
            patterns=comma_sep_to_list(args.file_patterns),
            git_provider=git_provider,
            target_branch=args.target_branch,
            check_only=args.check_only,
        )

        # Print the full commit sha
        if commit_sha:
            print(f"Commit Hash: {commit_sha}")

    except Exception as e:
        exit_code = handle_exception(e)

    sys.exit(exit_code)


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


# GitHub ref:
# https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
def is_github_actions() -> bool:
    var_value = os.getenv("GITHUB_ACTIONS")
    if var_value and var_value.lower() in ["true", "1"]:
        return True
    return False

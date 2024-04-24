# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""
This module creates reusable common options for Trestle Bot entrypoints.

All entrypoints should inherit from this class and use reusable_logic for interaction with the top-level
trestle bot logic located in trestlebot/bot.py.

The inheriting class should add required arguments for pre-task setup and
call the run_base method with the pre_tasks argument.
"""

import argparse
import logging
import sys
from typing import List, Optional

from trestlebot import const
from trestlebot.bot import TrestleBot
from trestlebot.github import GitHub, GitHubActionsResultsReporter, is_github_actions
from trestlebot.gitlab import (
    GitLab,
    GitLabCIResultsReporter,
    get_gitlab_root_url,
    is_gitlab_ci,
)
from trestlebot.provider import GitProvider
from trestlebot.reporter import BotResults, ResultsReporter
from trestlebot.tasks.base_task import TaskBase


logger = logging.getLogger(__name__)


class EntrypointBase:
    """Base class for all entrypoints."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self.parser: argparse.ArgumentParser = parser
        self.setup_common_arguments()

    def setup_common_arguments(self) -> None:
        """Setup arguments for the entrypoint."""
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Display verbose output",
            action="count",
            default=0,
        )
        self.parser.add_argument(
            "--branch",
            type=str,
            required=True,
            help="Branch name to push changes to",
        )
        self.parser.add_argument(
            "--working-dir",
            type=str,
            required=False,
            default=".",
            help="Working directory wit git repository",
        )
        self.parser.add_argument(
            "--file-patterns",
            required=False,
            type=str,
            default=".",
            help="Comma-separated list of file patterns to be used with `git add` in repository updates",
        )
        self.parser.add_argument(
            "--commit-message",
            type=str,
            required=False,
            default="chore: automatic updates",
            help="Commit message for automated updates",
        )
        self.parser.add_argument(
            "--pull-request-title",
            type=str,
            required=False,
            default="Automatic updates from trestlebot",
            help="Customized title for submitted pull requests",
        )
        self.parser.add_argument(
            "--committer-name",
            type=str,
            required=True,
            help="Name of committer",
        )
        self.parser.add_argument(
            "--committer-email",
            type=str,
            required=True,
            help="Email for committer",
        )
        self.parser.add_argument(
            "--author-name",
            required=False,
            type=str,
            help="Name for commit author if differs from committer",
        )
        self.parser.add_argument(
            "--author-email",
            required=False,
            type=str,
            help="Email for commit author if differs from committer",
        )
        self.parser.add_argument(
            "--dry-run",
            required=False,
            action="store_true",
            help="Run tasks, but do not push to the repository",
        )
        self.parser.add_argument(
            "--target-branch",
            type=str,
            required=False,
            help="Target branch or base branch to create a pull request against. \
            No pull request is created if unset",
        )
        self.parser.add_argument(
            "--with-token",
            nargs="?",
            type=argparse.FileType("r"),
            required=False,
            default=sys.stdin,
            help="Read token from standard input for authenticated requests with \
            Git provider (e.g. create pull requests)",
        )

    @staticmethod
    def set_git_provider(args: argparse.Namespace) -> Optional[GitProvider]:
        """Get the git provider based on the environment and args."""
        git_provider: Optional[GitProvider] = None
        if args.target_branch:
            if not args.with_token:
                raise EntrypointInvalidArgException(
                    "--with-token",
                    "with-token flag must be set when using target-branch",
                )

            if is_github_actions():
                git_provider = GitHub(access_token=args.with_token.read().strip())
            elif is_gitlab_ci():
                server_api_url = get_gitlab_root_url()
                git_provider = GitLab(
                    api_token=args.with_token.read().strip(), server_url=server_api_url
                )
            else:
                raise EntrypointInvalidArgException(
                    "--target-branch",
                    (
                        "target-branch flag is set with an unset git provider. "
                        "To test locally, set the GITHUB_ACTIONS or GITLAB_CI environment variable."
                    ),
                )
        return git_provider

    @staticmethod
    def set_reporter() -> ResultsReporter:
        """Get the reporter based on the environment and args."""
        if is_github_actions():
            return GitHubActionsResultsReporter()
        elif is_gitlab_ci():
            return GitLabCIResultsReporter()
        else:
            return ResultsReporter()

    def run_base(self, args: argparse.Namespace, pre_tasks: List[TaskBase]) -> None:
        """Reusable logic for all entrypoints."""

        git_provider: Optional[GitProvider] = self.set_git_provider(args)
        results_reporter: ResultsReporter = self.set_reporter()

        # Configure and run the bot
        bot = TrestleBot(
            working_dir=args.working_dir,
            branch=args.branch,
            commit_name=args.committer_name,
            commit_email=args.committer_email,
            author_name=args.author_name,
            author_email=args.author_email,
            target_branch=args.target_branch,
        )
        results: BotResults = bot.run(
            commit_message=args.commit_message,
            pre_tasks=pre_tasks,
            patterns=comma_sep_to_list(args.file_patterns),
            git_provider=git_provider,
            pull_request_title=args.pull_request_title,
            dry_run=args.dry_run,
        )

        # Report the results
        results_reporter.report_results(results)


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


class EntrypointInvalidArgException(Exception):
    """Custom exception for handling invalid arguments."""

    def __init__(self, arg: str, msg: str):
        super().__init__(f"Invalid args {arg}: {msg}")


def handle_exception(
    exception: Exception, msg: str = "Exception occurred during execution"
) -> int:
    """Log the exception and return the exit code"""
    logger.error(msg + f": {exception}")

    if isinstance(exception, EntrypointInvalidArgException):
        return const.INVALID_ARGS_EXIT_CODE

    return const.ERROR_EXIT_CODE

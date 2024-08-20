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
import os
import sys
from typing import List, Optional, Tuple

from trestlebot import const
from trestlebot.bot import TrestleBot
from trestlebot.github import GitHubActionsResultsReporter, is_github_actions
from trestlebot.gitlab import GitLabCIResultsReporter, get_gitlab_root_url, is_gitlab_ci
from trestlebot.provider import GitProvider
from trestlebot.provider_factory import GitProviderFactory
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
            "--working-dir",
            type=str,
            required=False,
            default=".",
            help="Working directory wit git repository",
        )
        self.parser.add_argument(
            "--dry-run",
            required=False,
            action="store_true",
            help="Run tasks, but do not push to the repository",
        )
        self._set_required_git_args()
        self._set_optional_git_args()
        self._set_git_provider_args()

    def _set_required_git_args(self) -> None:
        """Create an argument group for required git-related configuration."""
        required_git_arg_group = self.parser.add_argument_group(
            "required arguments for git operations"
        )
        required_git_arg_group.add_argument(
            "--branch",
            type=str,
            required=True,
            help="Branch name to push changes to",
        )
        required_git_arg_group.add_argument(
            "--committer-name",
            type=str,
            required=True,
            help="Name of committer",
        )
        required_git_arg_group.add_argument(
            "--committer-email",
            type=str,
            required=True,
            help="Email for committer",
        )

    def _set_optional_git_args(self) -> None:
        """Create an argument group for optional git-related configuration."""
        optional_git_arg_group = self.parser.add_argument_group(
            "optional arguments for git operations"
        )
        optional_git_arg_group.add_argument(
            "--file-patterns",
            required=False,
            type=str,
            default=".",
            help="Comma-separated list of file patterns to be used with `git add` in repository updates",
        )
        optional_git_arg_group.add_argument(
            "--commit-message",
            type=str,
            required=False,
            default="chore: automatic updates",
            help="Commit message for automated updates",
        )
        optional_git_arg_group.add_argument(
            "--author-name",
            required=False,
            type=str,
            help="Name for commit author if differs from committer",
        )
        optional_git_arg_group.add_argument(
            "--author-email",
            required=False,
            type=str,
            help="Email for commit author if differs from committer",
        )

    def _set_git_provider_args(self) -> None:
        """Create an argument group for optional git-provider configuration."""
        git_provider_arg_group = self.parser.add_argument_group(
            "optional arguments for interacting with the git provider"
        )

        # Detect default args for git provider type and server url
        detected_provider_type, detected_server_url = load_provider_from_environment()

        git_provider_arg_group.add_argument(
            "--target-branch",
            type=str,
            required=False,
            help="Target branch or base branch to create a pull request against. \
            No pull request is created if unset",
        )
        git_provider_arg_group.add_argument(
            "--with-token",
            required=False,
            nargs="?",
            type=argparse.FileType("r"),
            const=sys.stdin,
            help="Read token from standard input for authenticated requests with \
            Git provider (e.g. create pull requests)",
        )
        git_provider_arg_group.add_argument(
            "--pull-request-title",
            type=str,
            required=False,
            default="Automatic updates from trestlebot",
            help="Customized title for submitted pull requests",
        )
        git_provider_arg_group.add_argument(
            "--git-provider-type",
            required=False,
            choices=[const.GITHUB, const.GITLAB],
            default=detected_provider_type,
            help="Optional supported Git provider to identify. "
            "Defaults to auto detection based on pre-defined CI environment variables.",
        )
        git_provider_arg_group.add_argument(
            "--git-server-url",
            type=str,
            required=False,
            default=detected_server_url,
            help="Optional git server url for supported type. "
            "Defaults to auto detection based on pre-defined CI environment variables.",
        )

    @staticmethod
    def set_git_provider(args: argparse.Namespace) -> Optional[GitProvider]:
        """Get the git provider based on the environment and args."""
        git_provider: Optional[GitProvider] = None
        if args.target_branch:
            if args.with_token is None:
                # Attempts to read from env var
                access_token = os.environ.get("TRESTLEBOT_REPO_ACCESS_TOKEN", "")
                if not access_token:
                    raise EntrypointInvalidArgException(
                        "--with-token",
                        "with-token flag must be set to read from standard input or use "
                        "TRESTLEBOT_REPO_ACCESS_TOKEN environment variable when using target-branch",
                    )
            else:
                access_token = args.with_token.read()
            try:
                access_token = access_token.strip()
                git_provider_type = args.git_provider_type
                git_server_url = args.git_server_url
                if git_server_url and not git_provider_type:
                    raise EntrypointInvalidArgException(
                        "--git-provider-type",
                        "git-provider-type must be set when using git-server-url",
                    )
                git_provider = GitProviderFactory.provider_factory(
                    access_token, git_provider_type, git_server_url
                )
            except ValueError as e:
                raise EntrypointInvalidArgException("--git-server-url", str(e))
            except RuntimeError as e:
                raise EntrypointInvalidArgException(
                    "--target-branch, --git-provider-type", str(e)
                ) from e
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


def load_provider_from_environment() -> Tuple[str, str]:
    """
    Detect the Git provider from the environment.

    Returns:
        A tuple with the provider type string and server url string

    Note:
        The environment variables are expected to be pre-defined
        and set through the CI environment and not set by the user.
    """
    if is_github_actions():
        logger.debug("Detected GitHub Actions environment")
        return const.GITHUB, const.GITHUB_SERVER_URL
    elif is_gitlab_ci():
        logger.debug("Detected GitLab CI environment")
        return const.GITLAB, get_gitlab_root_url()
    return "", ""


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


class EntrypointInvalidArgException(Exception):
    """Custom exception for handling invalid arguments."""

    def __init__(self, arg: str, msg: str):
        super().__init__(f"Invalid args {arg}: {msg}")


def handle_exception(
    exception: Exception,
    traceback_str: str,
    msg: str = "Exception occurred during execution",
) -> int:
    """Log the exception and return the exit code"""
    logger.error(msg + f": {exception}")
    logger.debug(traceback_str)

    if isinstance(exception, EntrypointInvalidArgException):
        return const.INVALID_ARGS_EXIT_CODE

    return const.ERROR_EXIT_CODE

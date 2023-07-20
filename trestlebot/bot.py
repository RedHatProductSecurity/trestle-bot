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

"""This module implements functions for the Trestle Bot."""

import logging
from typing import List, Optional, Tuple

from git import GitCommandError
from git.repo import Repo
from git.util import Actor

from trestlebot.provider import GitProvider, GitProviderException
from trestlebot.tasks.base_task import TaskBase, TaskException


logger = logging.getLogger("trestle")


class RepoException(Exception):
    """An error requiring the user to perform a manual action in the
    destination repo
    """


def _stage_files(gitwd: Repo, patterns: List[str]) -> None:
    """Stages files in git based on file patterns"""
    for pattern in patterns:
        if pattern == ".":
            logger.info("Staging all repository changes")
            # Using check to avoid adding git directory
            # https://github.com/gitpython-developers/GitPython/issues/292
            gitwd.git.add(all=True)
            return
        else:
            logger.info(f"Adding file for pattern {pattern}")
            gitwd.git.add(pattern)


def _local_commit(
    gitwd: Repo,
    commit_user: str,
    commit_email: str,
    commit_message: str,
    author_name: str = "",
    author_email: str = "",
) -> str:
    """Creates a local commit in git working directory"""
    try:
        # Set the user and email for the commit
        gitwd.config_writer().set_value("user", "name", commit_user).release()
        gitwd.config_writer().set_value("user", "email", commit_email).release()

        author: Optional[Actor] = None

        if author_name and author_email:
            author = Actor(name=author_name, email=author_email)

        # Commit the changes
        commit = gitwd.index.commit(commit_message, author=author)

        # Return commit sha
        return commit.hexsha
    except GitCommandError as e:
        raise RepoException(f"Git commit failed: {e}") from e


def run(
    working_dir: str,
    branch: str,
    commit_name: str,
    commit_email: str,
    commit_message: str,
    author_name: str,
    author_email: str,
    patterns: List[str],
    git_provider: Optional[GitProvider] = None,
    pre_tasks: Optional[List[TaskBase]] = None,
    target_branch: str = "",
    pull_request_title: str = "Automatic updates from bot",
    check_only: bool = False,
    dry_run: bool = False,
) -> Tuple[str, int]:
    """Run Trestle Bot and returns commit and pull request information.

    Args:
         working_dir: Location of the git repo
         branch: Branch to put updates to
         commit_name: Name of the user for commit creation
         commit_email: Email of the user for commit creation
         commit_message: Customized commit message
         author_name: Name of the commit author
         author_email: Email of the commit author
         patterns: List of file patterns for `git add`
         git_provider: Optional configured git provider for interacting with the API
         pre_tasks: Optional task list to executing before updating the workspace
         target_branch: Optional target or base branch for submitted pull request
         pull_request_title: Optional customized pull request title
         check_only: Optional heck if the repo is dirty. Fail if true.
         dry_run: Only complete local work. Do not push.

    Returns:
        A tuple with commit_sha and pull request number.
        The commit_sha defaults to "" if there was no updates and the
        pull request number default to 0 if not submitted.
    """
    commit_sha: str = ""
    pr_number: int = 0

    # Execute bot pre-tasks before committing repository updates
    if pre_tasks is not None:
        for task in pre_tasks:
            try:
                task.execute()
            except TaskException as e:
                raise RepoException(f"Bot pre-tasks failed: {e}")

    # Create Git Repo
    repo = Repo(working_dir)

    # Check if there are any unstaged files
    if repo.is_dirty(untracked_files=True):
        if check_only:
            raise RepoException(
                "Check only mode is enabled and diff detected. "
                f"Manual intervention on {branch} is required."
            )

        _stage_files(repo, patterns)

        if repo.is_dirty():
            commit_sha = _local_commit(
                repo,
                commit_name,
                commit_email,
                commit_message,
                author_name,
                author_email,
            )

            if dry_run:
                logger.info("Dry run mode is enabled. Do not push to remote.")
                return commit_sha, pr_number

            try:
                # Get the remote repository by name
                remote = repo.remote()

                # Push changes to the remote repository
                remote.push(refspec=f"HEAD:{branch}")

                logger.info(f"Changes pushed to {branch} successfully.")

                # Only create a pull request if a GitProvider is configured and
                # a target branch is set.
                if git_provider is not None and target_branch:
                    logger.info(
                        f"Git provider detected, submitting pull request to {target_branch}"
                    )
                    # Parse remote url to get repository information for pull request
                    namespace, repo_name = git_provider.parse_repository(remote.url)
                    logger.debug("Detected namespace {namespace} and {repo_name}")

                    pr_number = git_provider.create_pull_request(
                        ns=namespace,
                        repo_name=repo_name,
                        head_branch=branch,
                        base_branch=target_branch,
                        title=pull_request_title,
                        body="",
                    )

                return commit_sha, pr_number

            except GitCommandError as e:
                raise RepoException(f"Git push to {branch} failed: {e}")
            except GitProviderException as e:
                raise RepoException(f"Git pull request to {target_branch} failed: {e}")
        else:
            logger.info("Nothing to commit")
            return commit_sha, pr_number
    else:
        logger.info("Nothing to commit")
        return commit_sha, pr_number

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
from typing import List, Optional

from git import GitCommandError
from git.repo import Repo
from git.util import Actor

from trestlebot.tasks.base_task import TaskBase, TaskException


logger = logging.getLogger("trestle")


class RepoException(Exception):
    """An error requiring the user to perform a manual action in the
    destination repo
    """


def _stage_files(gitwd: Repo, patterns: List[str]) -> None:
    """Stages files in git based on file patterns"""
    for pattern in patterns:
        gitwd.index.add(pattern)
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
    pre_tasks: Optional[List[TaskBase]] = None,
    check_only: bool = False,
    dry_run: bool = False,
) -> str:
    """Run Trestle Bot and return exit code

    Args:
         working_dir: Location of the git repo
         branch: Branch to put updates to
         commit_name: Name of the user for commit creation
         commit_email: Email of the user for commit creation
         author_name: Name of the commit author
         author_email: Email of the commit author
         patterns: List of file patterns for `git add`
         pre_tasks: Optional task list to executing before updating the workspace
         dry_run: Only complete local work. Do not push.

    Returns:
        A string containing the full commit sha. Defaults to "" if
        there was no updates
    """
    commit_sha: str = ""

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
                return commit_sha

            try:
                # Get the remote repository by name
                remote = repo.remote()

                # Push changes to the remote repository
                remote.push(refspec=f"HEAD:{branch}")

                logger.info(f"Changes pushed to {branch} successfully.")
                return commit_sha

            except GitCommandError as e:
                raise RepoException(f"Git push to {branch} failed: {e}") from e
        else:
            logger.info("Nothing to commit")
            return commit_sha
    else:
        logger.info("Nothing to commit")
        return commit_sha

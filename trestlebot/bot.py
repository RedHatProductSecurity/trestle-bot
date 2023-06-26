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
import sys
from typing import List, Optional

from git import GitCommandError
from git.repo import Repo
from git.util import Actor

from trestlebot.tasks.base_task import TaskBase, TaskException


logging.basicConfig(
    format="%(levelname)s - %(message)s", stream=sys.stdout, level=logging.INFO
)


class RepoException(Exception):
    """An error requiring the user to perform a manual action in the
    destination repo
    """


def _stage_files(gitwd: Repo, patterns: List[str]) -> None:
    """Stages files in git based on file patterns"""
    for pattern in patterns:
        logging.info(f"Adding file for pattern {pattern}")
        gitwd.index.add(pattern)


def _local_commit(
    gitwd: Repo,
    commit_user: str,
    commit_email: str,
    commit_message: str,
    author_name: str = "",
    author_email: str = "",
) -> None:
    """Creates a local commit in git working directory"""
    try:
        # Set the user and email for the commit
        gitwd.config_writer().set_value("user", "name", commit_user).release()
        gitwd.config_writer().set_value("user", "email", commit_email).release()

        author: Optional[Actor] = None

        if author_name and author_email:
            author = Actor(name=author_name, email=author_email)

        # Commit the changes
        gitwd.index.commit(commit_message, author=author)
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
    dry_run: bool = False,
) -> int:
    """Run Trestle Bot and return exit code"""

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
        _stage_files(repo, patterns)

        if repo.is_dirty():
            _local_commit(
                repo,
                commit_name,
                commit_email,
                commit_message,
                author_name,
                author_email,
            )

            if dry_run:
                logging.info("Dry run mode is enabled. Do not push to remote.")
                return 0

            try:
                # Get the remote repository by name
                remote = repo.remote()

                # Push changes to the remote repository
                remote.push(refspec=f"HEAD:{branch}")

                logging.info(f"Changes pushed to {branch} successfully.")
                return 0

            except GitCommandError as e:
                raise RepoException(f"Git push to {branch} failed: {e}") from e
        else:
            logging.info("Nothing to commit")
            return 0
    else:
        logging.info("Nothing to commit")
        return 0

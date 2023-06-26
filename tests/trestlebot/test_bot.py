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

"""Test for top-level Trestle Bot logic."""

import os
from typing import Tuple

from git.repo import Repo

import trestlebot.bot as bot
from tests.testutils import clean


def test_stage_files(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, repo = tmp_repo

    # Create test files
    with open(os.path.join(repo_path, "file1.txt"), "w") as f:
        f.write("Test file 1 content")
    with open(os.path.join(repo_path, "file2.txt"), "w") as f:
        f.write("Test file 2 content")

    # Stage the files
    bot._stage_files(repo, ["*.txt"])

    # Verify that files are staged
    staged_files = [item.a_path for item in repo.index.diff(repo.head.commit)]

    assert len(staged_files) == 2
    assert "file1.txt" in staged_files
    assert "file2.txt" in staged_files

    clean(repo_path, repo)


def test_local_commit(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    bot._local_commit(
        repo,
        commit_user="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
    )

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "Test User"
    assert commit.author.email == "test@example.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_local_commit_with_committer(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    bot._local_commit(
        repo,
        commit_user="Test Commit User",
        commit_email="test-committer@example.com",
        commit_message="Test commit message",
    )

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "Test Commit User"
    assert commit.author.email == "test-committer@example.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_local_commit_with_author(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    bot._local_commit(
        repo,
        commit_user="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
        author_name="The Author",
        author_email="author@test.com",
    )

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "The Author"
    assert commit.author.email == "author@test.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_run_dry_run(tmp_repo: Tuple[str, Repo]) -> None:
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    # Test running the bot
    bot.run(
        working_dir=repo_path,
        branch="main",
        commit_name="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
        author_name="The Author",
        author_email="author@test.com",
        patterns=["*.txt"],
        dry_run=True,
    )

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "The Author"
    assert commit.author.email == "author@test.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)

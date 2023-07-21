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

import json
import os
from typing import Tuple
from unittest.mock import Mock, patch

import pytest
from git.repo import Repo

import trestlebot.bot as bot
from tests.testutils import clean
from trestlebot.provider import GitProvider


def test_stage_files(tmp_repo: Tuple[str, Repo]) -> None:
    """Test staging files by patterns"""
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
    """Test local commit function"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    commit_sha = bot._local_commit(
        repo,
        commit_user="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
    )
    assert commit_sha != ""

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "Test User"
    assert commit.author.email == "test@example.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_local_commit_with_committer(tmp_repo: Tuple[str, Repo]) -> None:
    """Test setting committer information for commits"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    commit_sha = bot._local_commit(
        repo,
        commit_user="Test Commit User",
        commit_email="test-committer@example.com",
        commit_message="Test commit message",
    )

    assert commit_sha != ""

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "Test Commit User"
    assert commit.author.email == "test-committer@example.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_local_commit_with_author(tmp_repo: Tuple[str, Repo]) -> None:
    """Test setting author for commits"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.index.add(test_file_path)

    # Commit the test file
    commit_sha = bot._local_commit(
        repo,
        commit_user="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
        author_name="The Author",
        author_email="author@test.com",
    )
    assert commit_sha != ""

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "The Author"
    assert commit.author.email == "author@test.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_run(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with mocked push"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.return_value = "Mocked result"

        # Test running the bot
        commit_sha = bot.run(
            working_dir=repo_path,
            branch="main",
            commit_name="Test User",
            commit_email="test@example.com",
            commit_message="Test commit message",
            author_name="The Author",
            author_email="author@test.com",
            patterns=["*.txt"],
            dry_run=False,
        )
        assert commit_sha != ""

        # Verify that the commit is made
        commit = next(repo.iter_commits())
        assert commit.message.strip() == "Test commit message"
        assert commit.author.name == "The Author"
        assert commit.author.email == "author@test.com"
        mock_push.assert_called_once_with(refspec="HEAD:main")

        # Verify that the file is tracked by the commit
        assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_run_dry_run(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with dry run"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    # Test running the bot
    commit_sha = bot.run(
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
    assert commit_sha != ""

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "The Author"
    assert commit.author.email == "author@test.com"

    # Verify that the file is tracked by the commit
    assert os.path.basename(test_file_path) in commit.stats.files

    clean(repo_path, repo)


def test_empty_commit(tmp_repo: Tuple[str, Repo]) -> None:
    """Test running bot with no file updates"""
    repo_path, repo = tmp_repo

    # Test running the bot
    commit_sha = bot.run(
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
    assert commit_sha == ""

    clean(repo_path, repo)


def test_non_matching_files(tmp_repo: Tuple[str, Repo]) -> None:
    """Test that non-matching files are ignored"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    # Create a test file
    data = {"test": "file"}
    test_json_path = os.path.join(repo_path, "test.json")
    with open(test_json_path, "w") as f:
        json.dump(data, f, indent=4)

    # Test running the bot
    commit_sha = bot.run(
        working_dir=repo_path,
        branch="main",
        commit_name="Test User",
        commit_email="test@example.com",
        commit_message="Test commit message",
        author_name="The Author",
        author_email="author@test.com",
        patterns=["*.json"],
        dry_run=True,
    )
    assert commit_sha != ""

    # Verify that the commit is made
    commit = next(repo.iter_commits())
    assert commit.message.strip() == "Test commit message"
    assert commit.author.name == "The Author"
    assert commit.author.email == "author@test.com"

    # Verify that only the JSON file is tracked in the commits
    assert os.path.basename(test_file_path) not in commit.stats.files
    assert os.path.basename(test_json_path) in commit.stats.files

    clean(repo_path, repo)


def test_run_check_only(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with check_only"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    with pytest.raises(
        bot.RepoException,
        match="Check only mode is enabled and diff detected. Manual intervention on main is required.",
    ):
        _ = bot.run(
            working_dir=repo_path,
            branch="main",
            commit_name="Test User",
            commit_email="test@example.com",
            commit_message="Test commit message",
            author_name="The Author",
            author_email="author@test.com",
            patterns=["*.txt"],
            dry_run=True,
            check_only=True,
        )

    clean(repo_path, repo)


def test_run_with_provider(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with mock git provider"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    mock = Mock(spec=GitProvider)
    mock.create_pull_request.return_value = "10"
    mock.parse_repository.return_value = ("ns", "repo")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.return_value = "Mocked result"

        # Test running the bot
        commit_sha = bot.run(
            working_dir=repo_path,
            branch="test",
            commit_name="Test User",
            commit_email="test@example.com",
            commit_message="Test commit message",
            author_name="The Author",
            author_email="author@test.com",
            patterns=["*.txt"],
            git_provider=mock,
            target_branch="main",
            dry_run=False,
        )
        assert commit_sha != ""

        # Verify that the commit is made
        commit = next(repo.iter_commits())
        assert commit.message.strip() == "Test commit message"
        assert commit.author.name == "The Author"
        assert commit.author.email == "author@test.com"

        # Verify that the file is tracked by the commit
        assert os.path.basename(test_file_path) in commit.stats.files

        # Verify that the method was called with the expected arguments
        mock.create_pull_request.assert_called_once_with(
            ns="ns",
            repo_name="repo",
            head_branch="test",
            base_branch="main",
            title="Automatic updates from bot",
            body="",
        )
        mock_push.assert_called_once_with(refspec="HEAD:test")

    clean(repo_path, repo)


def test_run_with_provider_with_custom_pr_title(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with customer pull request title"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    mock = Mock(spec=GitProvider)
    mock.create_pull_request.return_value = "10"
    mock.parse_repository.return_value = ("ns", "repo")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.return_value = "Mocked result"

        # Test running the bot
        commit_sha = bot.run(
            working_dir=repo_path,
            branch="test",
            commit_name="Test User",
            commit_email="test@example.com",
            commit_message="Test commit message",
            author_name="The Author",
            author_email="author@test.com",
            patterns=["*.txt"],
            git_provider=mock,
            target_branch="main",
            pull_request_title="Test",
            dry_run=False,
        )
        assert commit_sha != ""

        # Verify that the commit is made
        commit = next(repo.iter_commits())
        assert commit.message.strip() == "Test commit message"
        assert commit.author.name == "The Author"
        assert commit.author.email == "author@test.com"

        # Verify that the file is tracked by the commit
        assert os.path.basename(test_file_path) in commit.stats.files

        # Verify that the method was called with the expected arguments
        mock.create_pull_request.assert_called_once_with(
            ns="ns",
            repo_name="repo",
            head_branch="test",
            base_branch="main",
            title="Test",
            body="",
        )
        mock_push.assert_called_once_with(refspec="HEAD:test")

    clean(repo_path, repo)

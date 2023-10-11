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
from typing import Callable, List, Tuple
from unittest.mock import Mock, patch

import pytest
from git import GitCommandError
from git.repo import Repo

import trestlebot.bot as bot
from trestlebot.provider import GitProvider, GitProviderException
from trestlebot.tasks.base_task import TaskBase, TaskException


def check_lists_equal(list1: List[str], list2: List[str]) -> bool:
    return sorted(list1) == sorted(list2)


@pytest.mark.parametrize(
    "file_patterns, expected_files",
    [
        (["*.txt"], ["file1.txt", "file2.txt"]),
        (["file*.txt"], ["file1.txt", "file2.txt"]),
        (["*.csv"], ["file3.csv"]),
        (["file*.csv"], ["file3.csv"]),
        (["*.txt", "*.csv"], ["file1.txt", "file2.txt", "file3.csv"]),
        (["."], ["file1.txt", "file2.txt", "file3.csv"]),
        ([], []),
    ],
)
def test_stage_files(
    tmp_repo: Tuple[str, Repo], file_patterns: List[str], expected_files: List[str]
) -> None:
    """Test staging files by patterns"""
    repo_path, repo = tmp_repo

    # Create test files
    with open(os.path.join(repo_path, "file1.txt"), "w") as f:
        f.write("Test file 1 content")
    with open(os.path.join(repo_path, "file2.txt"), "w") as f:
        f.write("Test file 2 content")
    with open(os.path.join(repo_path, "file3.csv"), "w") as f:
        f.write("test,")

    # Stage the files
    bot._stage_files(repo, file_patterns)

    # Verify that files are staged
    staged_files = [item.a_path for item in repo.index.diff(repo.head.commit)]

    assert check_lists_equal(staged_files, expected_files) is True


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
        commit_sha, pr_number = bot.run(
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
        assert pr_number == 0

        # Verify that the commit is made
        commit = next(repo.iter_commits())
        assert commit.message.strip() == "Test commit message"
        assert commit.author.name == "The Author"
        assert commit.author.email == "author@test.com"
        mock_push.assert_called_once_with(refspec="HEAD:main")

        # Verify that the file is tracked by the commit
        assert os.path.basename(test_file_path) in commit.stats.files


def test_run_dry_run(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with dry run"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.return_value = "Mocked result"

        # Test running the bot
        commit_sha, pr_number = bot.run(
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
        assert pr_number == 0

        mock_push.assert_not_called()


def test_empty_commit(tmp_repo: Tuple[str, Repo]) -> None:
    """Test running bot with no file updates"""
    repo_path, repo = tmp_repo

    # Test running the bot
    commit_sha, pr_number = bot.run(
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
    assert pr_number == 0


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
        _, _ = bot.run(
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


def push_side_effect(refspec: str) -> None:
    raise GitCommandError("example")


def pull_side_effect(refspec: str) -> None:
    raise GitProviderException("example")


@pytest.mark.parametrize(
    "side_effect, msg",
    [
        (push_side_effect, "Git push to .* failed: .*"),
        (pull_side_effect, "Git pull request to .* failed: example"),
    ],
)
def test_run_with_exception(
    tmp_repo: Tuple[str, Repo], side_effect: Callable[[str], None], msg: str
) -> None:
    """Test bot run with mocked push with side effects that throw exceptions"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.side_effect = side_effect

        with pytest.raises(bot.RepoException, match=msg):
            _ = bot.run(
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


def test_run_with_failed_pre_task(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with mocked task that fails"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    mock = Mock(spec=TaskBase)
    mock.execute.side_effect = TaskException("example")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with pytest.raises(bot.RepoException, match="Bot pre-tasks failed: example"):
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
            pre_tasks=[mock],
        )


def test_run_with_provider(tmp_repo: Tuple[str, Repo]) -> None:
    """Test bot run with mock git provider"""
    repo_path, repo = tmp_repo

    # Create a test file
    test_file_path = os.path.join(repo_path, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test content")

    mock = Mock(spec=GitProvider)
    mock.create_pull_request.return_value = 10
    mock.parse_repository.return_value = ("ns", "repo")

    repo.create_remote("origin", url="git.test.com/test/repo.git")

    with patch("git.remote.Remote.push") as mock_push:
        mock_push.return_value = "Mocked result"

        # Test running the bot
        commit_sha, pr_number = bot.run(
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
        assert pr_number == 10

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

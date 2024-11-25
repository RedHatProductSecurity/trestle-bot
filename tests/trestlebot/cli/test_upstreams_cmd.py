# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Unit tests for upstreams commands."""

import pathlib
from typing import Tuple

import pytest
from click.testing import CliRunner
from git import Repo

from tests.testutils import clean, prepare_upstream_repo
from trestlebot.cli.commands.upstream import upstream_cmd
from trestlebot.cli.config import (
    TrestleBotConfig,
    UpstreamConfig,
    load_from_file,
    write_to_file,
)


TEST_CATALOG = "simplified_nist_catalog"
TEST_CATALOG_PATH = "catalogs/simplified_nist_catalog/catalog.json"
TEST_PROFILE = "simplified_nist_profile"
TEST_PROFILE_PATH = "profiles/simplified_nist_profile/profile.json"


def test_config_get_upstream_by_url() -> None:
    """Test to confirm _get_upstream_by_url returns a single valid upstream from the config."""
    config = TrestleBotConfig(upstreams=[UpstreamConfig(url="https://test")])

    assert len(config.upstreams) == 1
    assert config.upstreams[0].url == "https://test"
    assert config.upstreams[0].include_models == ["*"]  # confirm default was set
    assert config.upstreams[0].exclude_models == []
    assert config.upstreams[0].skip_validation is False


def test_upstream_add_already_exists(tmp_repo: Tuple[str, Repo]) -> None:
    """Test upstream add fails if upstream already exists"""
    repo_path, repo = tmp_repo
    config_path = pathlib.Path(repo_path).joinpath(".trestlebot/config.yml")

    source: str = prepare_upstream_repo()
    url = f"{source}@main"
    config = TrestleBotConfig(
        committer_email="test@test",
        committer_name="test",
        upstreams=[UpstreamConfig(url=url)],
    )
    write_to_file(config, config_path)

    runner = CliRunner()
    result = runner.invoke(
        upstream_cmd,
        [
            "add",
            "--repo-path",
            repo_path,
            "--config",
            config_path,
            "--url",
            url,
            "--branch",
            "test",
        ],
    )
    assert (
        result.exit_code == 0
    )  # This does return success, it just skips the URLs already in the config

    assert f"{url} already exists. Edit {config_path} to update." in result.output


def test_upstream_add(tmp_repo: Tuple[str, Repo]) -> None:
    """Tests successful add of upstream"""
    repo_dir, repo = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    config_path = repo_path.joinpath(".trestlebot/config.yml")

    source: str = prepare_upstream_repo()
    url = f"{source}@main"
    config = TrestleBotConfig(
        committer_email="test@test",
        committer_name="test",
    )
    write_to_file(config, config_path)

    runner = CliRunner()
    result = runner.invoke(
        upstream_cmd,
        [
            "add",
            "--repo-path",
            repo_path,
            "--config",
            config_path,
            "--url",
            url,
            "--branch",
            "main",
            "--debug",
        ],
    )
    updated_config = load_from_file(config_path)
    if not updated_config:
        pytest.fail("Updated config not found")
        return

    assert len(updated_config.upstreams) == 1
    assert updated_config.upstreams[0].url == url
    assert updated_config.upstreams[0].include_models == ["*"]
    assert updated_config.upstreams[0].exclude_models == []
    assert updated_config.upstreams[0].skip_validation is False
    assert (
        updated_config.committer_email == "test@test"
    )  # sanity check this didn't change
    assert repo_path.joinpath(TEST_CATALOG_PATH).exists()
    assert repo_path.joinpath(TEST_PROFILE_PATH).exists()
    assert result.exit_code == 0
    clean(source, None)


def test_upstream_add_exclude_models(tmp_repo: Tuple[str, Repo]) -> None:
    """Test add upstream with exclude models"""

    repo_dir, repo = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    config_path = repo_path.joinpath(".trestlebot/config.yml")

    source: str = prepare_upstream_repo()
    url = f"{source}@main"
    config = TrestleBotConfig(
        committer_email="test@test",
        committer_name="test",
    )
    write_to_file(config, config_path)

    runner = CliRunner()
    result = runner.invoke(
        upstream_cmd,
        [
            "add",
            "--repo-path",
            repo_path,
            "--config",
            config_path,
            "--url",
            url,
            "--branch",
            "main",
            "--exclude-model",
            TEST_PROFILE,
        ],
    )

    updated_config = load_from_file(config_path)
    if not updated_config:
        pytest.fail("Updated config not found")
        return

    assert len(updated_config.upstreams) == 1
    assert updated_config.upstreams[0].url == url
    assert updated_config.upstreams[0].include_models == ["*"]
    assert updated_config.upstreams[0].exclude_models == [TEST_PROFILE]
    assert updated_config.upstreams[0].skip_validation is False
    assert (
        updated_config.committer_email == "test@test"
    )  # sanity check this didn't change

    assert repo_path.joinpath(TEST_CATALOG_PATH).exists()
    assert not repo_path.joinpath(TEST_PROFILE_PATH).exists()
    assert result.exit_code == 0


def test_upstream_sync_upstream_no_upstreams_in_config(
    tmp_repo: Tuple[str, Repo]
) -> None:
    """Test sync upstream with no upstreams in config file."""

    repo_dir, repo = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    config_path = repo_path.joinpath(".trestlebot/config.yml")

    source: str = prepare_upstream_repo()
    url = f"{source}@main"
    config = TrestleBotConfig(
        committer_email="test@test",
        committer_name="test",
    )
    write_to_file(config, config_path)

    runner = CliRunner()
    result = runner.invoke(
        upstream_cmd,
        [
            "sync",
            "--repo-path",
            repo_path,
            "--config",
            config_path,
            "--url",
            url,
            "--branch",
            "main",
        ],
    )
    assert (
        "No upstreams defined in trestlebot config.  Use `upstream add` command."
        in result.output
    )
    assert result.exit_code == 1


def test_upstream_sync_upstream_not_found(tmp_repo: Tuple[str, Repo]) -> None:
    """Test sync upstream with url not found."""

    repo_dir, repo = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    config_path = repo_path.joinpath(".trestlebot/config.yml")

    source: str = prepare_upstream_repo()
    url = f"{source}@main"
    config = TrestleBotConfig(
        committer_email="test@test",
        committer_name="test",
        upstreams=[UpstreamConfig(url="foo@bar")],
    )
    write_to_file(config, config_path)

    runner = CliRunner()
    result = runner.invoke(
        upstream_cmd,
        [
            "sync",
            "--repo-path",
            repo_path,
            "--config",
            config_path,
            "--url",
            url,
            "--branch",
            "main",
        ],
    )
    assert f"No upstream defined for {source}" in result.output
    assert result.exit_code == 1

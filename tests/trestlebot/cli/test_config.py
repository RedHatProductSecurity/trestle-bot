# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Unit tests for CLI config module"""
import pathlib

import pytest
import yaml

from trestlebot.cli.config import (
    TrestleBotConfig,
    TrestleBotConfigError,
    load_from_file,
    make_config,
    write_to_file,
)


@pytest.fixture
def config_obj() -> TrestleBotConfig:
    return TrestleBotConfig(repo_path="/tmp", markdown_dir="markdown")


def test_invalid_config_raises_errors() -> None:
    """Test create config with invalid directory to raise error."""

    with pytest.raises(TrestleBotConfigError) as ex:
        _ = make_config(dict(repo_path="0"))

    assert (
        str(ex.value)
        == "Invalid config value for repo_path. Path does not point to a directory."
    )


def test_make_config_raises_no_errors(tmp_init_dir: str) -> None:
    """Test create a valid config object."""
    config = make_config(dict(repo_path=tmp_init_dir, markdown_dir="markdown-test"))
    assert isinstance(config, TrestleBotConfig)
    assert config.repo_path == pathlib.Path(tmp_init_dir)
    assert config.markdown_dir == "markdown-test"


def test_config_to_dict(config_obj: TrestleBotConfig) -> None:
    """Config should serialize to a dict."""
    model_dict = config_obj.model_dump()
    assert isinstance(model_dict, dict)
    assert model_dict["repo_path"] == str(config_obj.repo_path)
    assert model_dict["markdown_dir"] == config_obj.markdown_dir


def test_config_write_to_file(config_obj: TrestleBotConfig, tmp_init_dir: str) -> None:
    """Test config is written to yaml file."""
    filepath = pathlib.Path(tmp_init_dir).joinpath("config.yml")
    write_to_file(config_obj, filepath)
    with open(filepath, "r") as f:
        yaml_data = yaml.safe_load(f)

    assert yaml_data == config_obj.model_dump()


def test_config_laod_from_file(config_obj: TrestleBotConfig, tmp_init_dir: str) -> None:
    """Test config is read from yaml file into config object."""
    filepath = pathlib.Path(tmp_init_dir).joinpath("config.yml")
    with filepath.open("w") as config_file:
        yaml.dump(config_obj.model_dump(), config_file)

    config = load_from_file(str(filepath))
    assert isinstance(config, TrestleBotConfig)
    assert config.model_dump() == config_obj.model_dump()

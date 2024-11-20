# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""
Trestle-bot CLI configuration module.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, DirectoryPath, ValidationError, model_serializer


logger = logging.getLogger(__name__)


class TrestleBotConfigError(Exception):
    """Custom error to better format pydantic exceptions.

    Example pydantic error dict: {'type': str, 'loc': tuple[str], 'msg': str, 'input': str}

    """

    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = list(map(self._format, errors))
        super().__init__(
            f"Trestle-bot config file contains {len(self.errors)} error(s)."
        )

    def _format(self, err: Dict[str, Any]) -> str:
        """Returns a formatted string with the error details."""
        msg = "Unable to load config."  # default message if we can't parse error

        if err.get("loc"):
            msg = f"Invalid config value for {err['loc'][0]}."
        if err.get("msg"):
            msg += f" {err['msg']}."  # Add error message details if present
        return msg

    def __str__(self) -> str:
        return "".join(self.errors)


class TrestleBotConfig(BaseModel):
    """Data model for trestle-bot configuration."""

    repo_path: Optional[DirectoryPath] = None
    markdown_dir: Optional[str] = None

    @model_serializer
    def _dict(self) -> Dict[str, Any]:
        """Returns a dict that can be safely loaded to yaml."""
        config_dict = {
            "repo_path": str(self.repo_path),
            "markdown_dir": str(self.markdown_dir),
        }
        return dict(
            filter(lambda item: item[1] not in (None, "None"), config_dict.items())
        )


def load_from_file(file: str) -> Optional[TrestleBotConfig]:
    """Load yaml file to trestlebot config object"""
    try:
        with open(file, "r") as config_file:
            config_yaml = yaml.safe_load(config_file)
            return TrestleBotConfig(**config_yaml)
    except ValidationError as ex:
        raise TrestleBotConfigError(ex.errors())
    except FileNotFoundError:
        return None


def write_to_file(config: TrestleBotConfig, file_path: Path) -> None:
    """Write config object to yaml file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w") as config_file:
            yaml.dump(config.dict(), config_file)
    except ValidationError as ex:
        raise TrestleBotConfigError(ex.errors())


def make_config(values: Dict[str, Any]) -> TrestleBotConfig:
    """Generates a new trestle-bot config object"""
    try:
        return TrestleBotConfig(**values)
    except ValidationError as ex:
        raise TrestleBotConfigError(ex.errors())


def update_config(config: TrestleBotConfig, update: Dict[str, Any]) -> TrestleBotConfig:
    """Returns a new config object with specified updates."""
    try:
        return config.model_copy(update=update)
    except ValidationError as ex:
        raise TrestleBotConfigError(ex.errors())

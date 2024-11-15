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
            msg += f" {err['msg']}"  # Add error message details if present
        return msg


class TrestleBotConfig(BaseModel):
    """Data model for trestle-bot configuration."""

    working_dir: Optional[DirectoryPath] = None
    markdown_dir: Optional[DirectoryPath] = None

    @model_serializer
    def _dict(self) -> Dict[str, Any]:
        """Returns a dict that can be safely loaded to yaml."""
        config_dict = {
            "working_dir": str(self.working_dir),
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


def write_to_file(config: TrestleBotConfig, file: str) -> Path:
    """Write config object to yaml file"""

    with open(file, "w") as config_file:
        yaml.dump(config.dict(), config_file)
    return Path(file)


def update_config(config: TrestleBotConfig, update: Dict[str, Any]) -> TrestleBotConfig:
    """Returns a new config object with specified updates."""
    return config.model_copy(update=update)

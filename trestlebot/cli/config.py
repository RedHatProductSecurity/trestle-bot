"""
Trestle-bot CLI configuration module.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, DirectoryPath, model_serializer


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


def load_from_file(file: str) -> TrestleBotConfig:
    """Load yaml file to trestlebot config object"""

    with open(file, "r") as config_file:
        config_yaml = yaml.safe_load(config_file)
        return TrestleBotConfig(**config_yaml)


def write_to_file(config: TrestleBotConfig, file: str) -> Path:
    """Write config object to yaml file"""

    with open(file, "w") as config_file:
        yaml.dump(config.dict(), config_file)
    return Path(file)


def update_config(config: TrestleBotConfig, update: Dict[str, Any]) -> TrestleBotConfig:
    """Returns a new config object with specified updates."""
    return config.model_copy(update=update)

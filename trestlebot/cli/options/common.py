# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""
Common command options for trestle-bot commands.
"""

import functools
import logging
import sys
import traceback
from typing import Any, Callable, Dict, Optional, Sequence, TypeVar

import click

from trestlebot.cli.config import TrestleBotConfigError, load_from_file
from trestlebot.cli.log import set_log_level
from trestlebot.const import ERROR_EXIT_CODE, TRESTLEBOT_CONFIG_DIR


F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def handle_exceptions(func: F) -> Any:
    def wrapper(*args: Sequence[Any], **kwargs: Dict[Any, Any]) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            traceback_str = traceback.format_exc()
            logger.error(f"Trestle-bot Error: {str(ex)}")
            logger.error(traceback_str)
            return ERROR_EXIT_CODE

    return wrapper


def debug_to_log_level(ctx: click.Context, param: str, value: str) -> None:
    """Sets logging level based on debug flag."""

    #  TODO: get log level from config file
    log_level = logging.DEBUG if value else logging.INFO
    set_log_level(log_level)


def load_config_to_ctx(ctx: click.Context, param: str, value: str) -> Optional[str]:
    """Load yaml config file into Click context to set default values.

    This will always run before other options because the --config is_eager is True.
    """
    try:
        config = load_from_file(value)
        if not config:
            logger.debug("No configuration file found.")
            return None
    except TrestleBotConfigError as ex:
        logger.error(str(ex))
        for err in ex.errors:
            logger.error(f"[!] {err}")
        sys.exit(ERROR_EXIT_CODE)

    if not ctx.default_map:
        ctx.default_map = (
            config.dict()
        )  # if default_map has not yet been set by another option
    else:
        ctx.default_map.update(config)
        logger.debug(f"Successfully loaded config file {value} into context.")
    return value


def common_options(f: F) -> Any:
    """
    Configures common options used across commands.
    """

    @click.pass_context
    @click.option(
        "--config",
        type=click.Path(),
        envvar="TRESTLEBOT_CONFIG",
        help="Path to trestlebot configuration file",
        default=f"{TRESTLEBOT_CONFIG_DIR}/config.yml",
        is_eager=True,
        callback=load_config_to_ctx,
    )
    @click.option(
        "--debug",
        default=False,
        is_flag=True,
        is_eager=True,
        envvar="TRESTLEBOT_DEBUG",
        help="Enable debug logging messages.",
        callback=debug_to_log_level,
    )
    @handle_exceptions
    @functools.wraps(f)
    def wrapper_common_options(*args: Sequence[Any], **kwargs: Dict[Any, Any]) -> Any:
        return f(*args, **kwargs)

    return wrapper_common_options

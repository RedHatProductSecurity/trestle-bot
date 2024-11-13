"""
Common command options for trestle-bot commands.
"""

import functools
import traceback
from typing import Any, Callable, Dict, Sequence, TypeVar

import click

from trestlebot.const import ERROR_EXIT_CODE


F = TypeVar("F", bound=Callable[..., Any])


def handle_exceptions(func: F) -> Any:
    def wrapper(*args: Sequence[Any], **kwargs: Dict[Any, Any]) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            traceback_str = traceback.format_exc()
            click.echo(f"Trestle-bot Error: {str(ex)}")  # TODO: use logger.info
            click.echo(traceback_str)  # TODO: use loggger.debug
            return ERROR_EXIT_CODE

    return wrapper


def common_options(f: F) -> F:
    """
    Configures common options used across commands.
    """

    @click.pass_context
    @handle_exceptions
    @functools.wraps(f)
    def wrapper_common_options(*args: Sequence[Any], **kwargs: Dict[Any, Any]) -> F:
        return f(*args, **kwargs)

    return wrapper_common_options

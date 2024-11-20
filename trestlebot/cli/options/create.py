"""
Module for common create commands
"""

import functools
from typing import Any, Callable, Dict, Sequence, TypeVar

import click


F = TypeVar("F", bound=Callable[..., Any])


def common_create_options(f: F) -> Any:
    """
    Configuring common create options decorator for SSP and CD command
    """

    @click.pass_context
    @click.option(
        "--profile-name",
        prompt="Name of trestle workspace to include",
        help="Name of profile in trestle workspace to include.",
    )
    @functools.wraps(f)
    def wrapper_common_create_options(
        *args: Sequence[Any], **kwargs: Dict[Any, Any]
    ) -> Any:
        return f(*args, **kwargs)

    return wrapper_common_create_options

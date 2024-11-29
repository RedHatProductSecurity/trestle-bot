from typing import Any, Callable, TypeVar

import click


F = TypeVar("F", bound=Callable[..., Any])


def autosync_options(f: F) -> F:
    """
    Configuring autosync options decorator for autosync operations
    """

    f = click.option(
        "--markdown-dir",
        help="Path to Trestle markdown files",
        type=str,
        required=True,
    )(f)
    f = click.option(
        "--skip-item",
        help="Glob pattern to skip when running tasks",
        type=str,
        multiple=True,
    )(f)
    f = click.option(
        "--skip-assemble",
        help="Skip assembly task",
        is_flag=True,
        default=False,
        show_default=True,
    )(f)
    f = click.option(
        "--skip-regenerate",
        help="Skip regenerate task",
        is_flag=True,
        default=False,
        show_default=True,
    )(f)
    f = click.option(
        "--version",
        help="Version of the OSCAL model to set during assembly into JSON",
        type=str,
    )(f)
    return f

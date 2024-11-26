from typing import Any, Callable, TypeVar

import click


F = TypeVar("F", bound=Callable[..., Any])


def autosync_options(f: F) -> F:
    """
    Configuring autosync options decorator for autosync operations
    """

    f = click.option(
        "--markdown-path",
        help="Path to Trestle markdown files",
        type=click.Path(exists=True),
        required=True,
    )(f)
    f = click.option(
        "--skip-items",
        help="Comma-separated list of glob patterns to skip when running tasks",
        type=str,
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
    f = click.option(
        "--dry-run",
        help="Run tasks, but do not push to the repository",
        is_flag=True,
    )(f)
    return f

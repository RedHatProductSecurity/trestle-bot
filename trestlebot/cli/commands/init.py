""""
Module for Trestle-bot init command
"""

import pathlib
import sys

import click

from trestlebot.cli.options.common import common_options
from trestlebot.const import ERROR_EXIT_CODE, TRESTLEBOT_CONFIG_DIR


@click.command(name="init", help="Initialize a new trestle-bot repo.")
@click.option(
    "--repo-dir",
    help="Path to git repo.  Used as working directory for authoring.",
    type=click.Path(exists=True),
)
@click.option(
    "--markdown-dir", help="Path to store markdown content.", type=click.Path()
)
@common_options
def init_cmd(ctx: click.Context, repo_dir: str, markdown_dir: str) -> None:
    """Command to initialize a new trestlebot repo"""

    need_to_prompt = any((not repo_dir, not markdown_dir))
    if need_to_prompt:

        click.echo("\n* Welcome to the Trestle-bot CLI *\n")
        click.echo(
            "Please provide the following values to initialize the "
            "workspace [press Enter for defaults].\n"
        )
        if not repo_dir:
            repo_dir = click.prompt(
                "Path to git repo", default=".", type=click.Path(exists=True)
            )
        if not markdown_dir:
            markdown_dir = click.prompt(
                "Path to store markdown content", default="./markdown"
            )

    root_dir: pathlib.Path = pathlib.Path(repo_dir)
    git_dir: pathlib.Path = root_dir.joinpath(pathlib.Path(".git"))
    if not git_dir.exists():
        click.echo(
            f"Initialization failed. Given directory {root_dir} is not a Git repository."
        )  # TODO: use logger.error
        sys.exit(ERROR_EXIT_CODE)

    trestlebot_dir = root_dir.joinpath(pathlib.Path(TRESTLEBOT_CONFIG_DIR))
    if trestlebot_dir.exists():
        click.echo(
            f"Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in {root_dir}"
        )  # TODO: use logger.error
        sys.exit(ERROR_EXIT_CODE)

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""""
Module for Trestle-bot init command
"""
import logging
import sys
from pathlib import Path

import click
from trestle.common.const import MODEL_DIR_LIST

from trestlebot.cli.options.common import common_options
from trestlebot.const import ERROR_EXIT_CODE, TRESTLEBOT_CONFIG_DIR


logger = logging.getLogger(__name__)


def dir_make_if_not(directory: str) -> None:
    """Makes directory if it does not already exists."""
    try:
        Path(directory).mkdir(parents=True)
        logger.debug(f"Created directory {directory}")
    except FileExistsError:
        logger.debug(f"Directory {directory} exists, skipping create.")


@click.command(name="init", help="Initialize a new trestle-bot repo.")
@click.option(
    "--working-dir",
    help="Path to git repo.  Used as working directory for authoring.",
    type=click.Path(exists=True),
)
@click.option(
    "--markdown-dir", help="Path to store markdown content.", type=click.Path()
)
@common_options
def init_cmd(
    ctx: click.Context, working_dir: str, markdown_dir: str, debug: bool, config: str
) -> None:
    """Command to initialize a new trestlebot repo"""

    need_to_prompt = any((not working_dir, not markdown_dir))
    if need_to_prompt:

        click.echo("\n* Welcome to the Trestle-bot CLI *\n")
        click.echo(
            "Please provide the following values to initialize the "
            "workspace [press Enter for defaults].\n"
        )
        if not working_dir:
            working_dir = click.prompt(
                "Path to git repo", default=".", type=click.Path(exists=True)
            )
        if not markdown_dir:
            markdown_dir = click.prompt(
                "Path to store markdown content", default="./markdown"
            )

    root_dir: Path = Path(working_dir)
    git_dir: Path = root_dir.joinpath(Path(".git"))
    if not git_dir.exists():
        logging.error(
            f"[!] Initialization failed. Given directory {root_dir} is not a Git repository."
        )
        sys.exit(ERROR_EXIT_CODE)

    trestlebot_dir = root_dir.joinpath(Path(TRESTLEBOT_CONFIG_DIR))
    if trestlebot_dir.exists():
        logger.error(
            f"[!] Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in {root_dir}"
        )
        sys.exit(ERROR_EXIT_CODE)

    model_dirs = list(map(lambda x: str(root_dir.joinpath(x)), MODEL_DIR_LIST))
    list(map(dir_make_if_not, model_dirs))

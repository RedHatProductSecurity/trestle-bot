# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""""
Module for Trestle-bot init command
"""
import argparse
import logging
import sys
from pathlib import Path

import click
from trestle.common import file_utils
from trestle.common.const import MODEL_DIR_LIST
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.init import InitCmd

from trestlebot.cli.options.common import common_options
from trestlebot.const import (
    ERROR_EXIT_CODE,
    TRESTLEBOT_CONFIG_DIR,
    TRESTLEBOT_KEEP_FILE,
)


logger = logging.getLogger(__name__)


def call_trestle_init(working_dir: str, debug: bool) -> None:
    """Call compliance-trestle to initialize workspace"""

    verbose = 1 if debug else 0
    trestle_args = argparse.Namespace(
        verbose=verbose,
        trestle_root=Path(working_dir),
        full=False,
        govdocs=True,
        local=False,
    )
    return_code = InitCmd()._run(trestle_args)
    if return_code == CmdReturnCodes.SUCCESS.value:
        logger.debug("Initialized trestle project successfully")
    else:
        logger.error(
            f"Initialization failed.  Unexpted trestle error: {CmdReturnCodes(return_code).name}"
        )
        sys.exit(ERROR_EXIT_CODE)


def dir_make_if_not(directory: str) -> None:
    """Makes directory if it does not already exists."""
    try:
        pathobj = Path(directory)
        pathobj.mkdir(parents=True)
        keep_file = pathobj.joinpath(Path(TRESTLEBOT_KEEP_FILE))
        file_utils.make_hidden_file(keep_file)
        logger.debug(f"Created directory {directory}")
    except FileExistsError:
        logger.debug(f"Directory {directory} exists, skipping create.")


@click.command(name="init", help="Initialize a new trestle-bot repo.")
@click.option(
    "--working-dir",
    help="Path to git repo.  Used as working directory for authoring.",
    type=click.Path(exists=True),
)
@click.option("--markdown-dir", help="Path to store markdown files.", type=click.Path())
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
                "Enter path to git repo (workspace directory)",
                default=".",
                type=click.Path(exists=True),
            )
        if not markdown_dir:
            markdown_dir = click.prompt(
                "Enter path to store markdown files", default="./markdown"
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

    # Create model directories in workspace root
    model_dirs = list(map(lambda x: str(root_dir.joinpath(x)), MODEL_DIR_LIST))
    list(map(dir_make_if_not, model_dirs))

    # Create markdown directories in workspace root
    markdown_dirs = list(
        map(lambda x: str(root_dir.joinpath(f"{markdown_dir}/" + x)), MODEL_DIR_LIST)
    )
    list(map(dir_make_if_not, markdown_dirs))

    call_trestle_init(working_dir, debug)

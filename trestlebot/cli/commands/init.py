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
from trestle.common.const import MODEL_DIR_LIST
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.init import InitCmd

from trestlebot.cli.config import make_config, write_to_file
from trestlebot.cli.options.common import common_options
from trestlebot.const import (
    ERROR_EXIT_CODE,
    TRESTLEBOT_CONFIG_DIR,
    TRESTLEBOT_KEEP_FILE,
)


logger = logging.getLogger(__name__)


def call_trestle_init(repo_path: Path, debug: bool) -> None:
    """Call compliance-trestle to initialize workspace"""

    verbose = 1 if debug else 0
    trestle_args = argparse.Namespace(
        verbose=verbose,
        trestle_root=repo_path,
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


@click.command(name="init", help="Initialize a new trestle-bot repo.")
@click.option(
    "--repo-path",
    "repo_path",
    help="Path to git repo.  Used as trestle root directory.",
    type=click.Path(path_type=Path, exists=True),
)
@click.option(
    "--markdown-dir", help="Directory name to store markdown files.", type=str
)
@common_options
def init_cmd(
    ctx: click.Context, repo_path: Path, markdown_dir: str, debug: bool, config: str
) -> None:
    """Command to initialize a new trestlebot repo"""

    need_to_prompt = any((not repo_path, not markdown_dir))
    if need_to_prompt:

        click.echo("\n* Welcome to the Trestle-bot CLI *\n")
        click.echo(
            "Please provide the following values to initialize the "
            "workspace [press Enter for defaults].\n"
        )
        if not repo_path:
            repo_path = click.prompt(
                "Enter path to git repo (workspace directory)",
                default=".",
                type=click.Path(path_type=Path, exists=True),
            )
        if not markdown_dir:
            markdown_dir = click.prompt(
                "Enter path to store markdown files", default="./markdown", type=str
            )

    git_path: Path = repo_path.joinpath(Path(".git"))
    if not git_path.exists():
        logging.error(
            f"Initialization failed. Given directory {repo_path} is not a Git repository."
        )
        sys.exit(ERROR_EXIT_CODE)

    trestlebot_dir = repo_path.joinpath(Path(TRESTLEBOT_CONFIG_DIR))
    if trestlebot_dir.exists():
        logger.error(
            f"Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in {repo_path}"
        )
        sys.exit(ERROR_EXIT_CODE)

    # Create model directories in workspace root
    list(
        map(
            lambda x: repo_path.joinpath(x)
            .joinpath(TRESTLEBOT_KEEP_FILE)
            .mkdir(parents=True, exist_ok=True),
            MODEL_DIR_LIST,
        )
    )
    logger.debug("Created model directories successfully")

    # Create markdown directories in workspace root
    list(
        map(
            lambda x: repo_path.joinpath(Path(markdown_dir))
            .joinpath(x)
            .joinpath(TRESTLEBOT_KEEP_FILE)
            .mkdir(parents=True, exist_ok=True),
            MODEL_DIR_LIST,
        )
    )
    logger.debug("Created markdown directories successfully")

    # inovke the init command in compliance trestle
    call_trestle_init(repo_path, debug)

    # generate and write trestle-bot cofig
    config = make_config(dict(repo_path=repo_path, markdown_dir=markdown_dir))
    config_path = trestlebot_dir.joinpath(Path("config.yml"))
    write_to_file(config, config_path)
    logger.debug(f"trestle-bot config file created at {str(config_path)}")
    logger.info(f"Successfully initialized trestlebot project in {repo_path}")

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

""""
Module for Trestle-bot init command
"""
import argparse
import logging
import os
import pathlib
import sys

import click
from trestle.common.const import MODEL_DIR_LIST
from trestle.common.file_utils import make_hidden_file
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
logging.getLogger("trestle.core.commands.init").setLevel("CRITICAL")


def call_trestle_init(repo_path: pathlib.Path, debug: bool) -> None:
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
            f"Initialization failed.  Unexpected trestle error: {CmdReturnCodes(return_code).name}"
        )
        sys.exit(ERROR_EXIT_CODE)


def mkdir_with_hidden_file(file_path: pathlib.Path) -> None:
    """Creates empty directory with .keep file"""
    file_path.parent.mkdir(exist_ok=True, parents=True)
    make_hidden_file(file_path)


@click.command(name="init", help="Initialize a new trestle-bot repo.")
@click.pass_context
@common_options
@click.option(
    "--repo-path",
    type=click.Path(path_type=pathlib.Path, exists=True),
    help="Path to Git repository to initialize.",
    default=os.getcwd(),
    prompt="Enter path to Git repository",
)  # override repo-path in common options to force prompt
@click.option(
    "--markdown-dir",
    type=str,
    help="Directory name to store markdown files.",
    default="markdown/",
    prompt="Enter path to store markdown files",
)
@click.option(
    "--default-committer-name",
    type=str,
    help="Default user name for Git commits.",
    default="",
    show_default=False,
    prompt="Enter default user name for Git commits (press <enter> to skip)",
)
@click.option(
    "--default-committer-email",
    type=str,
    help="Default user email for Git commits.",
    default="",
    show_default=False,
    prompt="Enter default user email for Git commits (press <enter> to skip)",
)
@click.option(
    "--default-commit-message",
    type=str,
    help="Default message for Git commits.",
    default="",
    show_default=False,
    prompt="Enter default message for Git commits (press <enter> to skip)",
)
@click.option(
    "--default-branch",
    type=str,
    help="Default repo branch to push automated changes.",
    default="",
    show_default=False,
    prompt="Enter default repo branch to push automated changes (press <enter> to skip)",
)
def init_cmd(
    ctx: click.Context,
    debug: bool,
    config_path: pathlib.Path,
    dry_run: bool,
    repo_path: pathlib.Path,
    markdown_dir: str,
    default_committer_name: str,
    default_committer_email: str,
    default_commit_message: str,
    default_branch: str,
) -> None:
    """Command to initialize a new trestlebot repo"""

    repo_path = repo_path.resolve()
    git_path: pathlib.Path = repo_path.joinpath(pathlib.Path(".git"))
    if not git_path.exists():
        logger.error(
            f"Initialization failed. Given directory {repo_path} is not a Git repository."
        )
        sys.exit(ERROR_EXIT_CODE)

    trestlebot_dir = repo_path.joinpath(pathlib.Path(TRESTLEBOT_CONFIG_DIR))
    if trestlebot_dir.exists():
        logger.error(
            f"Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in {repo_path}"
        )
        sys.exit(ERROR_EXIT_CODE)

    # Create model directories in workspace root
    list(
        map(
            lambda d: mkdir_with_hidden_file(
                repo_path.joinpath(d).joinpath(TRESTLEBOT_KEEP_FILE)
            ),
            MODEL_DIR_LIST,
        )
    )
    logger.debug("Created model directories successfully")

    # Create markdown directories in workspace root
    list(
        map(
            lambda d: mkdir_with_hidden_file(
                repo_path.joinpath(markdown_dir)
                .joinpath(d)
                .joinpath(TRESTLEBOT_KEEP_FILE)
            ),
            MODEL_DIR_LIST,
        )
    )
    logger.debug("Created markdown directories successfully")

    # invoke the init command in compliance trestle
    call_trestle_init(repo_path, debug)

    # generate and write trestle-bot config
    config_values = dict(repo_path=repo_path, markdown_dir=markdown_dir)
    if default_committer_name:
        config_values.update(committer_name=default_committer_name)

    if default_committer_email:
        config_values.update(committer_email=default_committer_email)

    if default_commit_message:
        config_values.update(commit_message=default_commit_message)

    if default_branch:
        config_values.update(branch=default_branch)

    config = make_config(config_values)
    if not config_path:
        config_path = trestlebot_dir.joinpath("config.yml")
    write_to_file(config, config_path)
    logger.debug(f"trestle-bot config file created at {str(config_path)}")
    logger.info(f"Successfully initialized trestlebot project in {repo_path}")

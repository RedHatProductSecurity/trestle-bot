# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Red Hat, Inc.

"""Module for sync cac catalog command"""
import logging
from pathlib import Path
from typing import Any, List

import click

from trestlebot.cli.options.common import common_options, git_options
from trestlebot.cli.utils import run_bot
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.sync_cac_catalog_task import SyncCacCatalogTask


logger = logging.getLogger(__name__)


@click.command(
    name="sync-cac-catalog",
    help="Transform CaC profile to OSCAL catalog.",
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--cac-content-root",
    help="Root of the CaC content project.",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
)
@click.option(
    "--cac-control",
    type=str,
    help="Name of the CaC control file.",
    required=True,
)
@click.option(
    "--oscal-catalog",
    type=str,
    help="Name of the catalog in the trestle workspace.",
    required=True,
)
def sync_cac_catalog_cmd(
    ctx: click.Context,
    cac_content_root: Path,
    cac_control: str,
    oscal_catalog: str,
    **kwargs: Any,
) -> None:
    """Transform CaC catalog to OSCAL catalog."""
    working_dir = kwargs["repo_path"]  # From common_options
    pre_tasks: List[TaskBase] = []
    sync_cac_content_task = SyncCacCatalogTask(
        cac_content_root=cac_content_root,
        cac_control=cac_control,
        oscal_catalog=oscal_catalog,
        working_dir=working_dir,
    )
    pre_tasks.append(sync_cac_content_task)
    result = run_bot(pre_tasks, kwargs)
    logger.debug(f"Trestlebot results: {result}")

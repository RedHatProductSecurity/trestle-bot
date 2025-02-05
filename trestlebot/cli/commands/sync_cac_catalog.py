# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac catalog command"""
import logging
from pathlib import Path
from typing import Any, List

import click

from trestle.oscal import common
from trestle.common import const
from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.utils import run_bot
from trestlebot.tasks.authored.catalog import AuthoredCatalog
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
    """Transform CaC catalog to OSCAL component definition."""
    # Steps:
    # 1. Check options, logger errors if any and exit.
    # 2. Initial product component definition with product name
    # 3. Create a new task to run the data transformation.
    # 4. Initialize a Trestlebot object and run the task(s).

    pre_tasks: List[TaskBase] = []

    working_dir = kwargs["repo_path"]


    authored_catalog = AuthoredCatalog(trestle_root=working_dir)
    # authored_catalog.create_update_cac_catalog(
    #     cac_catalog=cac_catalog,
    #     cac_content_root=cac_catalog_root,
    #     oscal_catalog=oscal_catalog,
    #     working_dir=working_dir,
    # )

    sync_cac_content_task = SyncCacCatalogTask(
        cac_content_root=cac_content_root,
        cac_control=cac_control,
        oscal_catalog=oscal_catalog,
        working_dir=working_dir,
    )

    pre_tasks.append(sync_cac_content_task)
    result = run_bot(pre_tasks, kwargs)
    logger.debug(f"Trestlebot results: {result}")


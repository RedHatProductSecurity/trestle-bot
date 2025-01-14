# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac content command"""
import logging
import os
import sys
import traceback
from typing import Any, List

import click

from trestlebot.cli.options.common import common_options, git_options
from trestlebot.cli.utils import run_bot
from trestlebot.const import ERROR_EXIT_CODE
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.sync_cac_content_task import SyncCacContentTask


logger = logging.getLogger(__name__)


@click.command(
    name="sync-cac-content",
    help="Transform CaC content to component definition in OSCAL.",
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--cac-content-root",
    help="Root of the CaC content project.",
    required=True,
)
@click.option(
    "--product",
    type=str,
    help="Product to build OSCAL component definition with",
    required=True,
)
@click.option(
    "--cac-profile",
    type=str,
    help="CaC profile used to collect product data for transformation",
    required=True,
)
@click.option(
    "--oscal-profile",
    type=str,
    help="Main profile href, or name of the profile in trestle workspace",
    required=True,
)
@click.option(
    "--component-definition-type",
    type=click.Choice(["service", "validation", "software"]),
    help="Type of component definition. Default: service",
    required=False,
    default="service",
)
def sync_cac_content_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Transform CaC content to OSCAL component definition."""

    product = kwargs["product"]
    cac_content_root = kwargs["cac_content_root"]
    component_definition_type = kwargs["component_definition_type"]
    cac_profile = os.path.join(cac_content_root, kwargs["cac_profile"])
    oscal_profile = kwargs["oscal_profile"]
    working_dir = str(kwargs["repo_path"].resolve())

    try:
        pre_tasks: List[TaskBase] = []
        authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
            trestle_root=working_dir,
        )
        sync_cac_content_task = SyncCacContentTask(
            product,
            cac_profile,
            cac_content_root,
            component_definition_type,
            oscal_profile,
            authored_comp,
        )
        pre_tasks.append(sync_cac_content_task)
        results = run_bot(pre_tasks, kwargs)
        logger.debug(f"Trestlebot results: {results}")
    except Exception as e:
        traceback_str = traceback.format_exc()
        logger.error(f"Trestle-bot Error: {str(e)}")
        logger.debug(traceback_str)
        sys.exit(ERROR_EXIT_CODE)

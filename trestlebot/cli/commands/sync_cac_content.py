# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac content command"""
import logging
from typing import Any

import click

from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition


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
    type=click.Choice(["service", "validation"]),
    help="Type of component definition. Default: service",
    required=False,
    default="service",
)
@handle_exceptions
def sync_cac_content_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Transform CaC content to OSCAL component definition."""
    # Steps:
    # 1. Check options, logger errors if any and exit.
    # 2. Initial product component definition with product name
    # 3. Create a new task to run the data transformation.
    # 4. Initialize a Trestlebot object and run the task(s).

    # pre_tasks: List[TaskBase] = []

    product = kwargs["product"]
    cac_content_root = kwargs["cac_content_root"]
    component_description = kwargs["product"]
    component_definition_type = kwargs.get("component_definition_type", "service")
    working_dir = kwargs["repo_path"]

    authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
        trestle_root=working_dir,
    )
    authored_comp.create_update_cac_compdef(
        comp_description=component_description,
        comp_type=component_definition_type,
        product=product,
        cac_content_root=cac_content_root,
        working_dir=working_dir,
    )

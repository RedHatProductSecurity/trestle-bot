# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac content command"""
import logging
from typing import Any, List

import click

from trestlebot import const
from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.utils import get_component_title, run_bot
from trestlebot.tasks.authored.compdef import (
    AuthoredComponentDefinition,
    FilterByProfile,
)
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


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
@click.option(
    "--markdown-dir",
    type=str,
    help="Directory name to store markdown files.",
    required=True,
)
@handle_exceptions
def sync_cac_content_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Transform CaC content to OSCAL component definition."""
    # Steps:
    # 1. Check options, logger errors if any and exit.
    # 2. Create a new task to run the data transformation.
    # 3. Initialize a Trestlebot object and run the task(s).

    pre_tasks: List[TaskBase] = []

    oscal_profile = kwargs["oscal_profile"]
    compdef_name = "cac-components"
    product = kwargs["product"]
    cac_content_root = kwargs["cac_content_root"]
    component_title = get_component_title(product, cac_content_root)
    component_description = kwargs["product"]
    filter_by_profile = kwargs.get("filter_by_profile")
    component_definition_type = kwargs.get("component_definition_type", "service")
    markdown_dir = kwargs["markdown_dir"]
    repo_path = kwargs["repo_path"]
    if filter_by_profile:
        filter_by_profile = FilterByProfile(repo_path, filter_by_profile)
    authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
        trestle_root=repo_path,
    )
    authored_comp.create_new_default(
        profile_name=oscal_profile,
        compdef_name=compdef_name,
        comp_title=component_title,
        comp_description=component_description,
        comp_type=component_definition_type,
        filter_by_profile=filter_by_profile,
    )
    logger.info(f"Component definition name is: {component_title}.")

    transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()

    model_filter: ModelFilter = ModelFilter(
        [], [compdef_name, component_title, f"{const.RULE_PREFIX}*"]
    )
    logger.info(f"model_filter is: {model_filter}.")

    rule_transform_task: RuleTransformTask = RuleTransformTask(
        working_dir=repo_path,
        rules_view_dir=const.RULES_VIEW_DIR,
        rule_transformer=transformer,
        model_filter=model_filter,
    )
    logger.info(
        f"Profile to filter controls in the component files is: {filter_by_profile}."
    )
    logger.debug(
        f"Oscal profile in use with the component definition is: {oscal_profile}."
    )
    logger.debug(f"Component definition type is {component_definition_type}.")

    pre_tasks.append(rule_transform_task)

    regenerate_task: RegenerateTask = RegenerateTask(
        authored_object=authored_comp,
        markdown_dir=markdown_dir,
        model_filter=model_filter,
    )
    pre_tasks.append(regenerate_task)

    run_bot(pre_tasks, kwargs)

    logger.debug(f"You have successfully authored the {compdef_name}.")

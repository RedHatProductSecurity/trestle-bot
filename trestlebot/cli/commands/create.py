"""
Module for create-cd create-ssp command for CLI
"""

import logging
from typing import Any, List

import click

from trestlebot import const
from trestlebot.cli.options.common import handle_exceptions
from trestlebot.cli.options.create import common_create_options
from trestlebot.cli.run import run
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored.compdef import (
    AuthoredComponentDefinition,
    FilterByProfile,
)
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


logger = logging.getLogger(__name__)


@click.group(name="create")
@common_create_options
@handle_exceptions
def create_cmd(ctx: click.Context, profile_name: str) -> None:
    """
    Command leveraged for component definition and ssp authoring in trestlebot.
    """

    pass


# @create_cmd.command(name="compdef", help="command for component definition authoring")
@create_cmd.command("compdef")
@click.option(
    "--compdef-name",
    prompt="Name of component definition is",
    help="Name of component definition.",
)
@click.option(
    "--component-title",
    prompt="The name of component title is",
    help="Title of initial component.",
)
@click.option(
    "--component-description",
    prompt="The description of the initial component is",
    help="Description of initial component.",
)
@click.option(
    "--filter-by-profile",
    required=False,
    help="Optionally filter the controls in the component definition by a profile",
)
@click.option(
    "--component-definition-type",
    default="service",
    help="Type of component definition",
)
@common_create_options
@handle_exceptions
def compdef_cmd(
    ctx: click.Context,
    **kwargs: Any,
) -> None:
    """
    Component definition authoring command.
    """
    pre_tasks: List[TaskBase] = []

    profile_name = kwargs["profile_name"]
    compdef_name = kwargs["compdef_name"]
    component_title = kwargs["component_title"]
    component_description = kwargs["component_description"]
    filter_by_profile = kwargs["filter_by_profile"]
    component_definition_type = kwargs["component_definition_type"]
    repo_path = kwargs["repo_path"]
    markdown_dir = kwargs["markdown_dir"]
    if filter_by_profile:
        filter_by_profile = FilterByProfile(repo_path, filter_by_profile)

    authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
        trestle_root=repo_path,
    )
    authored_comp.create_new_default(
        profile_name=profile_name,
        compdef_name=compdef_name,
        comp_title=component_title,
        comp_description=component_description,
        comp_type=component_definition_type,
        filter_by_profile=filter_by_profile,
    )
    transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()

    model_filter: ModelFilter = ModelFilter(
        [], [profile_name, component_title, f"{const.RULE_PREFIX}*"]
    )

    rule_transform_task: RuleTransformTask = RuleTransformTask(
        working_dir=repo_path,
        rules_view_dir=const.RULES_VIEW_DIR,
        rule_transformer=transformer,
        model_filter=model_filter,
    )
    pre_tasks.append(rule_transform_task)

    regenerate_task: RegenerateTask = RegenerateTask(
        authored_object=authored_comp,
        # trestle_root=repo_path,
        markdown_dir=markdown_dir,
        model_filter=model_filter,
    )
    pre_tasks.append(regenerate_task)

    run(pre_tasks, kwargs)

    logger.info(
        f"The name of the profile in use with the component definition is {profile_name}."
    )
    logger.info(
        f"You have selected component definitions as the document you want {compdef_name} to author."
    )
    logger.info(f"The component definition name is {component_title}.")
    logger.info(f"The component description to author is {component_description}.")
    logger.info(
        f"The profile you want to filter controls in the component files is {filter_by_profile}."
    )
    logger.info(f"The component definition type is {component_definition_type}.")


# @create_cmd.command(name="ssp", help="command for ssp authoring")
@create_cmd.command("ssp")
@click.option(
    "--ssp-name",
    prompt="Name of SSP to create",
    help="Name of SSP to create.",
)
@click.option(
    "--leveraged-ssp",
    help="Provider SSP to leverage for the new SSP.",
)
@click.option(
    "--ssp-index-path",
    default="ssp-index.json",
    help="Optionally set the path to the SSP index file.",
)
@click.option(
    "--yaml-header-path",
    default="ssp-index.json",
    help="Optionally set a path to a YAML file for custom SSP Markdown YAML headers.",
)
@common_create_options
@handle_exceptions
def ssp_cmd(
    ctx: click.Context,
    **kwargs: Any,
) -> None:
    """
    SSP Authoring command
    """

    profile_name = kwargs["profile_name"]
    ssp_name = kwargs["ssp_name"]
    leveraged_ssp = kwargs["leveraged_ssp"]
    ssp_index_path = kwargs["ssp_index_path"]
    yaml_header_path = kwargs["yaml_header_path"]
    repo_path = kwargs["repo_path"]
    markdown_dir = kwargs["markdown_dir"]
    compdefs = kwargs["None"]

    ssp_index: SSPIndex = SSPIndex(index_path=ssp_index_path)
    authored_ssp: AuthoredSSP = AuthoredSSP(trestle_root=repo_path, ssp_index=ssp_index)

    authored_ssp.create_new_default(
        profile_name=profile_name,
        ssp_name=ssp_name,
        compdefs=compdefs,
        markdown_path=markdown_dir,
        leveraged_ssp=leveraged_ssp,
        yaml_header=yaml_header_path,
    )

    # The starting point for SSPs is the markdown, so assemble into JSON.
    model_filter: ModelFilter = ModelFilter([], [ssp_name])
    assemble_task: AssembleTask = AssembleTask(
        authored_object=authored_ssp,
        markdown_dir=markdown_dir,
        # version=version,
        model_filter=model_filter,
    )
    # pre_tasks.append(assemble_task)

    pre_tasks: List[TaskBase] = [assemble_task]

    run(pre_tasks, kwargs)

    logger.info(f"The name of the profile in use with the SSP is {profile_name}.")
    logger.info(f"The SSP index path is {ssp_index_path}.")
    logger.info(f"The YAML file for custom SSP markdown is {yaml_header_path}.")

    logger.debug(f"The leveraged SSP is {leveraged_ssp}.")
    logger.debug(f"The name of the SSP to create is {ssp_name}.")

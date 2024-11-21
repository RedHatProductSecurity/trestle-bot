"""
Module for create-cd create-ssp command for CLI
"""

import logging

import click

from trestlebot.cli.options.create import common_create_options


logger = logging.getLogger(__name__)


@click.group(name="create")
@common_create_options
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
def compdef_cmd(
    ctx: click.Context,
    profile_name: str,
    compdef_name: str,
    component_title: str,
    component_description: str,
    filter_by_profile: str,
    component_definition_type: str,
) -> None:
    """
    Component definition authoring command.
    """
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
def ssp_cmd(
    ctx: click.Context,
    profile_name: str,
    ssp_name: str,
    leveraged_ssp: str,
    ssp_index_path: str,
    yaml_header_path: str,
) -> None:
    """
    SSP Authoring command
    """
    logger.info(f"The name of the profile in use with the SSP is {profile_name}.")
    logger.info(f"The name of the SSP to create is {ssp_name}.")
    logger.info(f"The leveraged SSP is {leveraged_ssp}.")
    logger.info(f"The SSP index path is {ssp_index_path}.")
    logger.info(f"The YAML file for custom SSP markdown is {yaml_header_path}.")

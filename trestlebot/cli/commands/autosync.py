""" Autosync command"""

import logging
from typing import Any, List

import click

from trestlebot.cli.options.autosync import autosync_options
from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.run import comma_sep_to_list
from trestlebot.cli.run import run as bot_run
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask


logger = logging.getLogger(__name__)


@handle_exceptions
def run(oscal_model: str, **kwargs: Any) -> None:
    """Run the autosync for oscal model."""

    pre_tasks: List[TaskBase] = []
    kwargs["working_dir"] = str(kwargs["repo_path"].resolve())
    if kwargs.get("file_patterns"):
        kwargs.update({"patterns": comma_sep_to_list(kwargs["file_patterns"])})
    model_filter: ModelFilter = ModelFilter(
        skip_patterns=comma_sep_to_list(kwargs.get("skip_items", "")),
        include_patterns=["*"],
    )
    authored_object: AuthoredObjectBase = types.get_authored_object(
        oscal_model,
        kwargs["working_dir"],
        kwargs.get("ssp_index_path", ""),
    )

    # Assuming an edit has occurred assemble would be run before regenerate.
    # Adding this to the list first
    if not kwargs.get("skip_assemble"):
        assemble_task: AssembleTask = AssembleTask(
            authored_object=authored_object,
            markdown_dir=kwargs["markdown_path"],
            version=kwargs.get("version", ""),
            model_filter=model_filter,
        )
        pre_tasks.append(assemble_task)
    else:
        logger.info("Assemble task skipped.")

    if not kwargs.get("skip_regenerate"):
        regenerate_task: RegenerateTask = RegenerateTask(
            authored_object=authored_object,
            markdown_dir=kwargs["markdown_path"],
            model_filter=model_filter,
        )
        pre_tasks.append(regenerate_task)
    else:
        logger.info("Regeneration task skipped.")
    bot_run(pre_tasks, kwargs)


@click.group(name="autosync", help="Autosync operations")
@click.pass_context
def autosync_cmd(ctx: click.Context) -> None:
    """Command to autosync catalog, profile, compdef and ssp."""


@autosync_cmd.command("ssp")
@click.pass_context
@common_options
@autosync_options
@git_options
@click.option(
    "--ssp-index-path",
    help="Path to ssp index file",
    type=str,
    required=True,
)
def autosync_ssp_cmd(ctx: click.Context, ssp_index_path: str, **kwargs: Any) -> None:
    kwargs.update({"ssp_index_path": ssp_index_path})
    run("ssp", **kwargs)


@autosync_cmd.command("compdef")
@click.pass_context
@common_options
@autosync_options
@git_options
def autosync_compdef_cmd(ctx: click.Context, **kwargs: Any) -> None:
    run("compdef", **kwargs)


@autosync_cmd.command("catalog")
@click.pass_context
@common_options
@autosync_options
@git_options
def autosync_catalog_cmd(ctx: click.Context, **kwargs: Any) -> None:
    run("catalog", **kwargs)


@autosync_cmd.command("profile")
@click.pass_context
@common_options
@autosync_options
@git_options
def autosync_profile_cmd(ctx: click.Context, **kwargs: Any) -> None:
    run("profile", **kwargs)

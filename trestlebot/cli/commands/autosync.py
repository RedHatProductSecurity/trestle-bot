""" Autosync command"""

import logging
from typing import Any, Dict, List

import click

from trestlebot.cli.options.common import git_options, handle_exceptions
from trestlebot.cli.run import comma_sep_to_list
from trestlebot.cli.run import run as bot_run
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask


logger = logging.getLogger(__name__)


@handle_exceptions
def run(oscal_model: str, ctx_obj: Dict[str, Any]) -> None:
    """Run the autosync for oscal model."""

    pre_tasks: List[TaskBase] = []
    # Allow any model to be skipped from the args, by default include all
    model_filter: ModelFilter = ModelFilter(
        skip_patterns=comma_sep_to_list(ctx_obj.get("skip_items", "")),
        include_patterns=["*"],
    )
    authored_object: AuthoredObjectBase = types.get_authored_object(
        oscal_model,
        ctx_obj["working_dir"],
        ctx_obj.get("ssp_index_path", ""),
    )

    # Assuming an edit has occurred assemble would be run before regenerate.
    # Adding this to the list first
    if not ctx_obj.get("skip_assemble"):
        assemble_task: AssembleTask = AssembleTask(
            authored_object=authored_object,
            markdown_dir=ctx_obj["markdown_path"],
            version=ctx_obj.get("version", ""),
            model_filter=model_filter,
        )
        pre_tasks.append(assemble_task)
    else:
        logger.info("Assemble task skipped.")

    if not ctx_obj.get("skip_regenerate"):
        regenerate_task: RegenerateTask = RegenerateTask(
            authored_object=authored_object,
            markdown_dir=ctx_obj["markdown_path"],
            model_filter=model_filter,
        )
        pre_tasks.append(regenerate_task)
    else:
        logger.info("Regeneration task skipped.")

    bot_run(pre_tasks, ctx_obj)


@click.group(name="autosync", help="Autosync operations")
@click.option(
    "--working-dir",
    help="Working directory wit git repository",
    type=click.Path(exists=True),
    prompt="Enter path to git repo (workspace directory)",
    default=".",
)  # TODO: use path in config
@click.option(
    "--markdown-path",
    help="Path to Trestle markdown files",
    type=click.Path(exists=True),
    prompt="Enter path to to Trestle markdown files",
)
@click.option(
    "--skip-items",
    help="Comma-separated list of glob patterns to skip when running tasks",
    type=str,
)
@click.option(
    "--skip-assemble",
    help="Skip assembly task",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "--skip-regenerate",
    help="Skip regenerate task",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "--version",
    help="Version of the OSCAL model to set during assembly into JSON",
    type=str,
)
@click.option(
    "--dry-run",
    help="Run tasks, but do not push to the repository",
    is_flag=True,
)
@git_options
@click.pass_context
def autosync_cmd(
    ctx: click.Context,
    working_dir: str,
    markdown_path: str,
    dry_run: bool,
    skip_items: str,
    skip_assemble: bool,
    skip_regenerate: bool,
    file_patterns: str,
    branch: str,
    commit_message: str,
    committer_name: str,
    committer_email: str,
    author_name: str,
    author_email: str,
    version: str,
) -> None:
    """Command to autosync catalog, profile, compdef and ssp."""

    ctx.obj = dict(
        working_dir=working_dir,
        markdown_path=markdown_path,
        skip_items=skip_items,
        skip_assemble=skip_assemble,
        skip_regenerate=skip_regenerate,
        version=version,
        patterns=comma_sep_to_list(file_patterns),
        branch=branch,
        commit_message=commit_message,
        committer_name=committer_name,
        committer_email=committer_email,
        author_name=author_name,
        author_email=author_email,
        dry_run=dry_run,
    )


@autosync_cmd.command("ssp")
@click.option(
    "--ssp-index-path",
    help="Path to ssp index file",
    type=click.File("r"),
)
@click.pass_context
def autosync_ssp_cmd(ctx: click.Context, ssp_index_path: str) -> None:
    if not ssp_index_path:
        ssp_index_path = click.prompt(
            "Enter path to ssp index file",
            type=click.Path(exists=True),
        )
    ctx.obj.update(
        {
            "ssp_index_path": ssp_index_path,
        }
    )
    run("ssp", ctx.obj)


@autosync_cmd.command("compdef")
@click.pass_context
def autosync_compdef_cmd(ctx: click.Context) -> None:
    run("compdef", ctx.obj)


@autosync_cmd.command("catalog")
@click.pass_context
def autosync_catalog_cmd(ctx: click.Context) -> None:
    run("catalog", ctx.obj)


@autosync_cmd.command("profile")
@click.pass_context
def autosync_profile_cmd(ctx: click.Context) -> None:
    run("profile", ctx.obj)

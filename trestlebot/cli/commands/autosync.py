""" Autosync command"""

import argparse

import click

from trestlebot.cli.base import comma_sep_to_list, run
from trestlebot.cli.options.common import git_options


@click.group(name="autosync", help="Autosync operations")
@click.option(
    "--working-dir",
    help="Working directory wit git repository",
    type=click.Path(exists=True),
)
@click.option(
    "--dry-run",
    help="Run tasks, but do not push to the repository",
    is_flag=True,
)
@click.option(
    "--markdown-path",
    help="Path to Trestle markdown files",
    type=click.Path(exists=True),  # Should it exist?
)
@click.option(
    "--skip-items",
    help="Comma-separated list of glob patterns to skip when running tasks",
    type=str,  # What's the type?
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

    need_to_prompt = any(
        (
            not working_dir,
            not markdown_path,
            not branch,
            not committer_email,
            not committer_name,
        )
    )
    if need_to_prompt:
        click.echo("\n* Welcome to the Trestle-bot CLI *\n")
        click.echo("Please provide the following values to start autosync operations.")
        if not working_dir:
            working_dir = click.prompt(
                "Enter path to working directory wit git repository",
                default=".",
                type=click.Path(exists=True),
            )
        if not markdown_path:
            markdown_path = click.prompt(
                "Enter path to to Trestle markdown files",
                type=click.Path(exists=True),
            )
        if not branch:
            branch = click.prompt(
                "Enter branch name to push changes to",
            )
        if not committer_email:
            committer_email = click.prompt(
                "Enter email for committer",
            )
        if not committer_name:
            committer_name = click.prompt(
                "Enter name of committer",
            )

    ctx.trestle_args = argparse.Namespace(
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
        # target_branch=target_branch,
        # pull_request_title=pull_request_title,
        dry_run=dry_run,
    )


@autosync_cmd.command("ssp")
@click.pass_context
@click.option("--ssp-index-path", help="Path to ssp index file", type=click.File("r"))
def autosync_ssp_cmd(ctx: click.Context, ssp_index_path: str) -> None:
    if not ssp_index_path:
        ssp_index_path = click.prompt(
            "Enter path to ssp index file",
            type=click.Path(exists=True),
        )
    run("ssp", ctx.parent.trestle_args, ssp_index_path)


@autosync_cmd.command("compdef")
@click.pass_context
def autosync_compdef_cmd(ctx: click.Context) -> None:
    run("compdef", ctx.parent.trestle_args)


@autosync_cmd.command("catalog")
@click.pass_context
def autosync_catalog_cmd(ctx: click.Context) -> None:
    run("catalog", ctx.parent.trestle_args)


@autosync_cmd.command("profile")
@click.pass_context
def autosync_profile_cmd(ctx: click.Context) -> None:
    run("profile", ctx.parent.trestle_args)

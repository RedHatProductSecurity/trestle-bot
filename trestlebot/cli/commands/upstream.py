# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for upstream command"""
import logging
import pathlib
import sys
from typing import Any, List, Optional

import click

from trestlebot.cli.config import (
    TrestleBotConfig,
    UpstreamConfig,
    load_from_file,
    make_config,
    write_to_file,
)
from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.run import run
from trestlebot.const import ERROR_EXIT_CODE
from trestlebot.reporter import BotResults
from trestlebot.tasks.base_task import ModelFilter
from trestlebot.tasks.sync_upstreams_task import SyncUpstreamsTask


logger = logging.getLogger(__name__)


def sync_upstream_for_url(
    repo_path: pathlib.Path,
    dry_run: bool,
    url: str,
    include_models: List[str],
    exclude_models: List[str],
    skip_validation: bool,
    committer_name: str,
    committer_email: str,
    branch: str,
) -> BotResults:
    """Invoke the sync upstream task for a given URL."""
    model_filter: ModelFilter = ModelFilter(
        include_patterns=include_models, skip_patterns=exclude_models
    )

    validate = not skip_validation

    sync_upstreams_task = SyncUpstreamsTask(
        working_dir=str(repo_path.resolve()),
        git_sources=[url],
        model_filter=model_filter,
        validate=validate,
    )
    kwargs = dict(
        working_dir=(str(repo_path.resolve())),
        committer_name=committer_name,
        committer_email=committer_email,
        branch=branch,
        dry_run=dry_run,
    )
    return run([sync_upstreams_task], kwargs)


def _config_get_upstream_by_url(
    config: TrestleBotConfig, url: str
) -> Optional[UpstreamConfig]:
    """Returns one upstream that matches url, else None."""
    if config.upstreams:
        for upstream in config.upstreams:
            if upstream.url == url:
                return upstream
    return None


@click.group(name="upstream")
@click.pass_context
def upstream_cmd(ctx: click.Context) -> None:
    """Sync content from upstream git repositories."""


@upstream_cmd.command(
    name="add", help="Add new upstream repository and download content."
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--url",
    type=str,
    help="Upstream repo URL in the form <repo_url>@<ref> where ref is a git ref such as tag or branch.",
    required=True,
    multiple=True,
)
@click.option(
    "--exclude-model",
    type=str,
    help="Glob pattern for model names to exclude (e.g. --exclude-model=profile_y*).",
    required=False,
    multiple=True,
)
@click.option(
    "--include-model",
    type=str,
    help="Glob pattern for model names to include (e.g. --include-model=profile_y*).",
    required=False,
    multiple=True,
)
@click.option(
    "--skip-validation",
    type=bool,
    help="Skip validation of the models when they are copied.",
    is_flag=True,
)
@handle_exceptions
def upstream_add_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Add new upstream sources to workspace."""

    repo_path = kwargs["repo_path"]
    url_list = list(kwargs["url"])

    config_path: pathlib.Path = kwargs["config_path"]
    config = load_from_file(config_path)
    if not config:
        # No config exists or was not found, create a new one
        logger.warning(
            f"No trestlebot config file found, creating {str(config_path.resolve())}"
        )
        config = make_config()

    for url in url_list:
        existing_urls = [upstream.url for upstream in config.upstreams]
        if url in existing_urls:
            logger.warning(
                f"Upstream for {url} already exists. Edit {config_path} to update."
            )
            continue

        include_models = list(kwargs.get("include_model", ["*"]))
        if len(include_models) == 0:
            include_models = [
                "*"
            ]  # This needs to be set otherwise the task will not include any models
        exclude_models = list(kwargs.get("exclude_model", []))
        skip_validation = kwargs.get("skip_validation", False)
        result = sync_upstream_for_url(
            repo_path=repo_path,
            dry_run=kwargs["dry_run"],
            url=url,
            include_models=include_models,
            exclude_models=exclude_models,
            skip_validation=skip_validation,
            committer_name=kwargs["committer_name"],
            committer_email=kwargs["committer_email"],
            branch=kwargs["branch"],
        )
        logger.debug(f"Bot results for {url}: {result}")

        config.upstreams.append(
            UpstreamConfig(
                url=url,
                include_models=include_models,
                exclude_models=exclude_models,
                skip_validation=skip_validation,
            )
        )
        logger.info(f"Added {url} to trestlebot workspace")

    write_to_file(config, config_path)


@upstream_cmd.command(
    name="sync", help="Sync content from an added upstream repository."
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--url",
    type=str,
    help="Upstream repo URL in the form <repo_url>@<ref> where ref is a git ref such as tag or branch.",
    required=False,
    multiple=True,
)
@click.option(
    "--all",
    type=str,
    help="URL to GitHub repo containing upstream content.",
    required=False,
    is_flag=True,
)
@handle_exceptions
def upstream_sync_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Sync upstream sources to local workspace"""

    config_path: pathlib.Path = kwargs["config_path"]
    config = load_from_file(config_path)
    if not config or len(config.upstreams) == 0:
        logger.error(
            "No upstreams defined in trestlebot config.  Use `upstream add` command."
        )
        sys.exit(ERROR_EXIT_CODE)

    upstreams_to_sync = []
    if kwargs.get("all"):
        upstreams_to_sync = config.upstreams

    elif urls := kwargs.get("url"):
        for url in urls:
            if upstream := _config_get_upstream_by_url(config, url):
                upstreams_to_sync.append(upstream)

            else:
                logger.error(f"No upstream defined for {url} - skipping!")

    else:
        logger.error("Must specify --url <git@ref> or --all to sync all upstreams")
        sys.exit(ERROR_EXIT_CODE)

    if len(upstreams_to_sync) == 0:
        logger.error("No upstreams found to sync.")
        sys.exit(ERROR_EXIT_CODE)

    for upstream in upstreams_to_sync:

        result = sync_upstream_for_url(
            repo_path=kwargs["repo_path"],
            dry_run=kwargs["dry_run"],
            url=upstream.url,
            include_models=upstream.include_models,
            exclude_models=upstream.exclude_models,
            skip_validation=upstream.skip_validation,
            committer_name=kwargs["committer_name"],
            committer_email=kwargs["committer_email"],
            branch=kwargs["branch"],
        )
        logger.debug(f"Bot results for {upstream.url}: {result}")
    logger.info("Sync from upstreams complete")

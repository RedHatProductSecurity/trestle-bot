# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

import logging
from typing import Any, Dict, List

from ssg.products import load_product_yaml, product_yaml_path

from trestlebot.bot import TrestleBot
from trestlebot.reporter import BotResults
from trestlebot.tasks.base_task import TaskBase


logger = logging.getLogger(__name__)


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


def run_bot(pre_tasks: List[TaskBase], kwargs: Dict[Any, Any]) -> BotResults:
    """Reusable logic for all commands."""

    # Configure and run the bot
    bot = TrestleBot(
        working_dir=kwargs["repo_path"],
        branch=kwargs["branch"],
        commit_name=kwargs["committer_name"],
        commit_email=kwargs["committer_email"],
        author_name=kwargs.get("author_name", ""),
        author_email=kwargs.get("author_email", ""),
    )

    return bot.run(
        pre_tasks=pre_tasks,
        patterns=kwargs.get("patterns", ["."]),
        commit_message=kwargs.get(
            "commit_message", "Automatic updates from trestle-bot"
        ),
        dry_run=kwargs.get("dry_run", False),
    )


def get_component_title(product_name: str, cac_path: str) -> str:
    """Get the product name from product yml file via the SSG library."""
    if product_name and cac_path:
        # Get the product yaml file path
        product_yml_path = product_yaml_path(cac_path, product_name)
        # Load the product data
        product = load_product_yaml(product_yml_path)
        # Return product name from product yml file
        return product._primary_data.get("product")
    else:
        raise ValueError("component_title is empty or None")

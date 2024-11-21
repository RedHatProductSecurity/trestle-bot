from typing import Any, Dict, List

from trestlebot.bot import TrestleBot
from trestlebot.tasks.base_task import TaskBase


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


def run(pre_tasks: List[TaskBase], kwargs: Dict[Any, Any]) -> None:
    """Reusable logic for all commands."""
    # Configure and run the bot
    bot = TrestleBot(
        working_dir=kwargs["working_dir"],
        branch=kwargs["branch"],
        commit_name=kwargs["committer_name"],
        commit_email=kwargs["committer_email"],
        author_name=kwargs.get("author_name", ""),
        author_email=kwargs.get("author_email", ""),
    )
    bot.run(
        pre_tasks=pre_tasks,
        patterns=comma_sep_to_list(kwargs.get("patterns", "")),
        commit_message=kwargs.get("commit_message", "Automatic updates from bot"),
        dry_run=kwargs.get("dry_run", False),
    )

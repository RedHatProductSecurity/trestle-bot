import argparse
import logging
from typing import List

from trestlebot.bot import TrestleBot
from trestlebot.cli.options.common import handle_exceptions
from trestlebot.tasks.assemble_task import AssembleTask
from trestlebot.tasks.authored import types
from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask


logger = logging.getLogger(__name__)


def comma_sep_to_list(string: str) -> List[str]:
    """Convert comma-sep string to list of strings and strip."""
    string = string.strip() if string else ""
    return list(map(str.strip, string.split(","))) if string else []


def run_base(args: argparse.Namespace, pre_tasks: List[TaskBase]) -> None:
    """Reusable logic for all commands."""
    # from trestlebot.reporter import BotResults, ResultsReporter
    # git_provider: Optional[GitProvider] = self.set_git_provider(args)
    # results_reporter: ResultsReporter = self.set_reporter()

    # Configure and run the bot
    bot = TrestleBot(
        working_dir=args.working_dir,
        branch=args.branch,
        commit_name=args.committer_name,
        commit_email=args.committer_email,
        author_name=args.author_name,
        author_email=args.author_email,
        # target_branch=args.target_branch,
    )
    # results: BotResults = bot.run(
    bot.run(
        pre_tasks=pre_tasks,
        patterns=comma_sep_to_list(args.patterns),
        commit_message=args.commit_message,
        # git_provider=git_provider,
        # pull_request_title=args.pull_request_title,
        dry_run=args.dry_run,
    )

    # # Report the results
    # results_reporter.report_results(results)


@handle_exceptions
def run(oscal_model: str, args: argparse.Namespace, ssp_index_path: str = "") -> None:
    """Run the autosync for oscal model."""

    pre_tasks: List[TaskBase] = []
    # Allow any model to be skipped from the args, by default include all
    model_filter: ModelFilter = ModelFilter(
        skip_patterns=comma_sep_to_list(args.skip_items),
        include_patterns=["*"],
    )
    authored_object: AuthoredObjectBase = types.get_authored_object(
        oscal_model, args.working_dir, ssp_index_path
    )

    # Assuming an edit has occurred assemble would be run before regenerate.
    # Adding this to the list first
    if not args.skip_assemble:
        assemble_task: AssembleTask = AssembleTask(
            authored_object=authored_object,
            markdown_dir=args.markdown_path,
            version=args.version,
            model_filter=model_filter,
        )
        pre_tasks.append(assemble_task)
    else:
        logger.info("Assemble task skipped.")

    if not args.skip_regenerate:
        regenerate_task: RegenerateTask = RegenerateTask(
            authored_object=authored_object,
            markdown_dir=args.markdown_path,
            model_filter=model_filter,
        )
        pre_tasks.append(regenerate_task)
    else:
        logger.info("Regeneration task skipped.")

    run_base(args, pre_tasks)

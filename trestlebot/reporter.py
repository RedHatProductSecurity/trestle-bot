# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Results reporting for the Trestle Bot."""

from dataclasses import dataclass
from typing import List


@dataclass
class BotResults:
    """A dataclass to hold the results of the bot run"""

    changes: List[str]
    commit_sha: str
    pr_number: int


class ResultsReporter:
    """
    Class for generate output for results reporting.
    """

    def report_results(self, results: BotResults) -> str:
        """Report the results of the Trestle Bot."""
        results_str = "Results:"
        if results.changes:
            results_str = results_str + "\nChanges:"
            for change in results.changes:
                results_str = results_str + f"\n{change}"

        if results.commit_sha:
            results_str = results_str + f"\nCommit Hash: {results.commit_sha}"

        if results.pr_number:
            results_str = results_str + f"\nPull Request Number: {results.pr_number}"

        return results_str

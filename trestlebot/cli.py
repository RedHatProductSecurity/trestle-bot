#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""This module parses CLI arguments for the Trestle Bot."""

import argparse
import sys

from trestlebot import bot


def _parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automation git actions for compliance-trestle"
    )
    parser.add_argument(
        "--branch",
        type=str,
        required=True,
        help="Branch name to push changes to",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=False,
        default=".",
        help="Working directory wit git repository",
    )
    parser.add_argument(
        "--committer-name",
        type=str,
        required=True,
        help="Name of committer",
    )
    parser.add_argument(
        "--committer-email",
        type=str,
        required=True,
        help="Email for committer",
    )
    parser.add_argument(
        "--author-name",
        required=False,
        type=str,
        default="",
        help="Name for commit author if differs from committer",
    )
    parser.add_argument(
        "--author-email",
        required=False,
        type=str,
        default="",
        help="Email for commit author if differs from committer",
    )
    parser.add_argument(
        "--patterns", nargs="+", type=str, required=True, help="List of file patterns"
    )
    return parser.parse_args()


def run():
    """Trestle Bot entry point function."""
    args = _parse_cli_arguments()
    success = bot.run(
        working_dir=args.working_dir,
        branch=args.branch,
        commit_name=args.committer_name,
        commit_email=args.committer_email,
        author_name=args.author_name,
        author_email=args.author_email,
        patterns=args.patterns,
    )

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

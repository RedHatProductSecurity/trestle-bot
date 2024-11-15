# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""Main entrypoint for trestlebot"""

import click

from trestlebot.cli.commands.init import init_cmd


EPILOG = "See our docs at https://redhatproductsecurity.github.io/trestle-bot"

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    name="trestlebot",
    help="Trestle-bot CLI",
    context_settings=CONTEXT_SETTINGS,
    epilog=EPILOG,
)
@click.pass_context
def root_cmd(ctx: click.Context) -> None:
    """Root command"""


root_cmd.add_command(init_cmd)

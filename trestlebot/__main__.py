# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


# Default entrypoint for trestlebot is autosync mode when run with python -m trestlebot

from trestlebot.entrypoints.autosync import main as autosync_main


def init() -> None:
    """Initialize trestlebot"""
    if __name__ == "__main__":
        autosync_main()


init()

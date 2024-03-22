# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Configure logger for trestlebot and trestle."""

import argparse
import logging
import sys

import trestle.common.log as log


_logger = logging.getLogger("trestlebot")


def set_log_level_from_args(args: argparse.Namespace) -> None:
    """Set the log level from the args for trestle and trestlebot."""

    # Setup the trestle logger
    log.set_log_level_from_args(args=args)

    if args.verbose == 1:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)


def configure_logger(level: int = logging.INFO) -> None:
    """Configure the logger."""
    _logger.setLevel(level=level)

    # Create a StreamHandler to send non-error logs to stdout
    stdout_info_handler = logging.StreamHandler(sys.stdout)
    stdout_info_handler.setLevel(logging.INFO)

    stdout_debug_handler = logging.StreamHandler(sys.stdout)
    stdout_debug_handler.setLevel(logging.DEBUG)

    # Create a StreamHandler to send error logs to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    # Create a formatter and set it on both handlers
    detailed_formatter = logging.Formatter(
        "%(name)s:%(lineno)d %(levelname)s: %(message)s"
    )
    stdout_debug_handler.setFormatter(detailed_formatter)
    stderr_handler.setFormatter(detailed_formatter)

    _logger.addHandler(stdout_debug_handler)
    _logger.addHandler(stdout_info_handler)
    _logger.addHandler(stderr_handler)

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
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    # Create a StreamHandler to send error logs to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    # Create a formatter and set it on both handlers
    log_formatter = logging.Formatter("%(name)s:%(lineno)d %(levelname)s: %(message)s")
    stdout_handler.setFormatter(log_formatter)
    stderr_handler.setFormatter(log_formatter)

    _logger.addHandler(stdout_handler)
    _logger.addHandler(stderr_handler)

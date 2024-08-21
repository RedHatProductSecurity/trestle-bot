# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.


"""
This module provides the `init` entrypoint for trestlebot.

The init command is used for creating a new trestlebot workspace.  The command
will do the following:
    - create the .trestlebot directory for trestlebot related files
    - create files for use with the specified CICD provider
    - create the appropriate directories for the specified OSCAL model
    - run the trestle init command to generate the needed compliance-trestle directories
"""

import argparse
import logging
import pathlib
import shutil
import sys
import traceback

import importlib_resources
from trestle.common import file_utils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.init import InitCmd

from trestlebot.const import (
    ERROR_EXIT_CODE,
    GITHUB,
    GITHUB_WORKFLOWS_DIR,
    GITLAB,
    SUCCESS_EXIT_CODE,
    TRESTLEBOT_CONFIG_DIR,
    TRESTLEBOT_KEEP_FILE,
)
from trestlebot.entrypoints.entrypoint_base import handle_exception
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.authored import types as model_types


logger = logging.getLogger(__name__)
logging.getLogger("trestle.core.commands.init").setLevel("CRITICAL")

OSCAL_MODEL_SSP = model_types.AuthoredType.SSP.value
OSCAL_MODEL_COMPDEF = model_types.AuthoredType.COMPDEF.value


class InitEntrypoint:
    """Entrypoint for the init command."""

    TEMPLATES_MODULE = "trestlebot.entrypoints.templates"
    SUPPORTED_PROVIDERS = [GITHUB, GITLAB]
    SUPPORTED_MODELS = [
        OSCAL_MODEL_SSP,
        OSCAL_MODEL_COMPDEF,
    ]
    PROVIDER_TEMPLATES = {
        GITHUB: {
            OSCAL_MODEL_SSP: [
                "trestlebot-autosync-catalog.yml",
                "trestlebot-autosync-profile.yml",
            ],
            OSCAL_MODEL_COMPDEF: [
                "trestlebot-create-component-definition.yml",
                "trestlebot-autosync-catalog.yml",
                "trestlebot-autosync-profile.yml",
                "trestlebot-rules-transform.yml",
            ],
        }
    }
    MODEL_DIRS = {
        OSCAL_MODEL_SSP: [
            "system-security-plans",
            "component-definitions",
            "catalogs",
            "profiles",
        ],
        OSCAL_MODEL_COMPDEF: [
            "component-definitions",
            "catalogs",
            "profiles",
            "rules",
        ],
    }

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self.parser: argparse.ArgumentParser = parser
        self.setup_init_arguments()

    def setup_init_arguments(self) -> None:
        """Setup arguments for the init entrypoint."""
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Display verbose output",
            action="count",
            default=0,
        )
        self.parser.add_argument(
            "--working-dir",
            type=str,
            required=False,
            default=".",
            help="Working directory wit git repository",
        )
        self.parser.add_argument(
            "--provider",
            required=False,
            type=str,
            choices=self.SUPPORTED_PROVIDERS,
            default="github",
            help="Name of CI/CD provider",
        )
        self.parser.add_argument(
            "--oscal-model",
            required=True,
            type=str,
            choices=self.SUPPORTED_MODELS,
            help="OSCAL model type to run tasks on.",
        )

    def _call_trestle_init(self, args: argparse.Namespace) -> None:
        """Call compliance-trestle to initialize workspace"""
        trestle_args = argparse.Namespace(
            verbose=args.verbose,
            trestle_root=pathlib.Path(args.working_dir),
            full=False,
            govdocs=True,
            local=False,
        )
        return_code = InitCmd()._run(trestle_args)
        if return_code == CmdReturnCodes.SUCCESS.value:
            logger.debug("Initialized trestle project successfully")
        else:
            logger.error(
                f"Initialization failed.  Unexpted trestle error: {CmdReturnCodes(return_code).name}"
            )
            sys.exit(ERROR_EXIT_CODE)

    def _create_directories(self, args: argparse.Namespace) -> None:
        """Initialize trestlebot directories"""

        root = pathlib.Path(args.working_dir)
        model_dirs = self.MODEL_DIRS[args.oscal_model]

        for model_dir in model_dirs:
            directory = root.joinpath(pathlib.Path(model_dir))
            directory.mkdir(exist_ok=True)
            keep_file = directory.joinpath(pathlib.Path(TRESTLEBOT_KEEP_FILE))
            file_utils.make_hidden_file(keep_file)

    def _copy_provider_files(self, args: argparse.Namespace) -> None:
        """Copy the CICD provider files to the new trestlebot workspace"""
        if args.provider == GITHUB:
            provider_dir = pathlib.Path(args.working_dir).joinpath(
                pathlib.Path(GITHUB_WORKFLOWS_DIR)
            )
            provider_dir.mkdir(parents=True, exist_ok=True)

        templates_dir = importlib_resources.files(
            f"{self.TEMPLATES_MODULE}.{args.provider}"
        )
        for template_file in self.PROVIDER_TEMPLATES[args.provider][args.oscal_model]:
            template_path = templates_dir.joinpath(template_file)
            dest_path = provider_dir.joinpath(pathlib.Path(template_file))
            shutil.copyfile(str(template_path), dest_path)

    def run(self, args: argparse.Namespace) -> None:
        """Run the init entrypoint"""
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)
            root: pathlib.Path = pathlib.Path(args.working_dir)
            if not root.exists() or not root.is_dir():
                logger.error(
                    f"Initialization failed. Given directory {root} does not exist."
                )
                sys.exit(ERROR_EXIT_CODE)

            git_dir: pathlib.Path = root.joinpath(pathlib.Path(".git"))
            if not git_dir.exists():  # TODO: add --force flag to bypass
                logger.error(
                    f"Initialization failed. Given directory {root} is not a Git repository."
                )
                sys.exit(ERROR_EXIT_CODE)

            trestlebot_dir = root.joinpath(pathlib.Path(TRESTLEBOT_CONFIG_DIR))
            if trestlebot_dir.exists():
                logger.error(
                    f"Initialization failed. Found existing {TRESTLEBOT_CONFIG_DIR} directory in {root}"
                )
                sys.exit(ERROR_EXIT_CODE)
            else:
                trestlebot_dir.mkdir(parents=True, exist_ok=False)
                keep_file = trestlebot_dir / TRESTLEBOT_KEEP_FILE
                file_utils.make_hidden_file(keep_file)

            self._create_directories(args)
            self._call_trestle_init(args)
            self._copy_provider_files(args)

        except Exception as e:
            traceback_str = traceback.format_exc()
            exit_code = handle_exception(e, traceback_str)

        logger.info(f"Initialized trestlebot project successfully in {root}")
        sys.exit(exit_code)


def main() -> None:
    """Run the init entrypoint CLI."""
    parser = argparse.ArgumentParser(
        description="Workflow automation bot for compliance-trestle"
    )

    init = InitEntrypoint(parser=parser)
    args = parser.parse_args()
    init.run(args)


if __name__ == "__main__":
    main()

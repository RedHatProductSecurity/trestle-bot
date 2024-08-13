import argparse
import errno
import logging
import pathlib
import sys
import traceback
from typing import List

from trestle.common import file_utils
from trestle.core.commands.init import InitCmd

from trestlebot.const import (
    ERROR_EXIT_CODE,
    TRESTLEBOT_CONFIG_DIR,
    TRESTLEBOT_KEEP_FILE,
)
from trestlebot.entrypoints.entrypoint_base import EntrypointBase, handle_exception
from trestlebot.tasks.authored import types


logger = logging.getLogger(__name__)
logging.getLogger("trestle.core.commands.init").setLevel("CRITICAL")


class InitEntrypoint(EntrypointBase):
    """Entrypoint for the init command."""

    SUPPORTED_PROVIDERS = ["github", "gitlab"]
    SUPPORTED_MODELS = [types.AuthoredType.SSP.value, types.AuthoredType.COMPDEF.value]

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super().__init__(
            parser,
            required_git_args=False,
            optional_git_args=False,
            provider_git_args=False,
        )
        self.setup_init_arguments()

    def setup_init_arguments(self) -> None:
        """Setup arguments for the init entrypoint."""
        self.parser.add_argument(
            "--provider",
            required=True,
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

    def _model_to_dirs(self, model: str) -> List[str]:
        """Returns a list fo directories to create for a given OSCAL model type."""
        MODEL_DIRS = {
            "ssp": [
                "system-security-plan",
                "component-definitions",
                "catalog",
                "profile",
            ],
            "compdef": [
                "component-definitions",
                "catalog",
                "profile",
            ],
        }
        return MODEL_DIRS[model]

    def _trestle_init(self, args: argparse.Namespace) -> None:
        """Call compliance-trestle to initialize workspace"""
        logger.debug("Calling compliance-trestle init command")
        trestle_args = argparse.Namespace(
            verbose=args.verbose,
            trestle_root=pathlib.Path(args.working_dir),
            full=False,
            govdocs=True,
            local=False,
        )
        InitCmd()._run(trestle_args)
        logger.info("Trestle workspace init complete")

    def _trestlebot_init(self, args: argparse.Namespace) -> None:
        """Initialize trestlebot directories"""
        root = pathlib.Path(args.working_dir)

        # If trestlebot has already been initialized then exit
        try:
            trestlebot_dir = root / pathlib.Path(TRESTLEBOT_CONFIG_DIR)
            trestlebot_dir.mkdir(parents=True, exist_ok=False)
            keep_file = trestlebot_dir / TRESTLEBOT_KEEP_FILE
            file_utils.make_hidden_file(keep_file)
        except OSError as e:
            if e.errno == errno.EEXIST:
                logger.warning(
                    "Error: .trestlebot directory already exists in this workspace"
                )
                sys.exit(ERROR_EXIT_CODE)
            else:
                raise e

        model_dirs = self._model_to_dirs(args.oscal_model)
        for model_dir in model_dirs:
            directory = root / pathlib.Path(model_dir)
            directory.mkdir(parents=True, exist_ok=False)

    def run(self, args: argparse.Namespace) -> None:
        """Run the init entrypoint"""
        try:
            self._trestlebot_init(args)
            self._trestle_init(args)

        except Exception as e:
            traceback_str = traceback.format_exc()
            exit_code = handle_exception(e, traceback_str)
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

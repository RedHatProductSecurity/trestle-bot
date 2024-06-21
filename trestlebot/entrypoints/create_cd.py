#!/usr/bin/python

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""
Entrypoint for component definition bootstrapping.

This will create a rules-view directory in the working directory, create a component
definition in JSON format with the initially generated rules and initial trestle control markdown.
"""

import argparse
import logging
import pathlib
import sys
from typing import List, Optional

from trestlebot.const import RULE_PREFIX, RULES_VIEW_DIR, SUCCESS_EXIT_CODE
from trestlebot.entrypoints.entrypoint_base import EntrypointBase, handle_exception
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.authored.compdef import (
    AuthoredComponentDefinition,
    FilterByProfile,
)
from trestlebot.tasks.base_task import ModelFilter, TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer


logger = logging.getLogger(__name__)


class CreateCDEntrypoint(EntrypointBase):
    """Entrypoint for component definition bootstrapping."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        super().__init__(parser)
        self.setup_create_cd_arguments()

    def setup_create_cd_arguments(self) -> None:
        """Setup specific arguments for this entrypoint."""
        self.parser.add_argument(
            "--profile-name",
            required=False,
            help="Name of profile in the trestle workspace to use with the component definition.",
        )
        self.parser.add_argument(
            "--compdef-name", required=True, help="Name of component definition"
        )
        self.parser.add_argument(
            "--component-title", required=False, help="Title of initial component"
        )
        self.parser.add_argument(
            "--component-description",
            required=False,
            help="Description of initial component",
        )
        self.parser.add_argument(
            "--markdown-path",
            required=True,
            type=str,
            help="Path to create markdown files in.",
        )
        self.parser.add_argument(
            "--component-definition-type",
            required=False,
            type=str,
            choices=[
                "interconnection",
                "service",
                "software",
                "hardware",
                "policy",
                "physical",
                "process-procedure",
                "plan",
                "guidance",
                "standard",
                "validation",
            ],
            default="service",
            help="Type of component definition",
        )
        self.parser.add_argument(
            "--filter-by-profile",
            required=False,
            type=str,
            help="Optionally filter the controls in the component definition by a profile.",
        )

        self._setup_validation_component_args()

    def _setup_validation_component_args(self) -> None:
        """Adds arguments for creating validation component definitions."""
        validation_cd_arg_group = self.parser.add_argument_group(
            "required arguments for creating a validation component definition"
        )
        validation_cd_arg_group.add_argument(
            "--product-component-definition",
            type=argparse.FileType("r"),
            required=False,
            help="Existing product component definition file.",
        )
        validation_cd_arg_group.add_argument(
            "--product-component-title",
            required=False,
            help="Existing product component to map to validation component.",
        )

    def validate_args(self, args: argparse.Namespace) -> None:
        """Validates arguments passed to the CLI."""
        required_args = ["profile_name", "component_title", "component_description"]

        if args.component_definition_type == "validation":
            required_args = ["product_component_definition"]

        missing_args = []
        for arg in required_args:
            if vars(args).get(arg) is None:
                missing_args.append(arg)

        if len(missing_args) > 0:
            # produce an error that matches the default argparse format
            formatted_args = [f"--{i.replace('_', '-')}" for i in missing_args]
            args_msg = ", ".join(formatted_args)
            self.parser.error(f"the following arguments are required: {args_msg}")

    def run(self, args: argparse.Namespace) -> None:
        """Run the entrypoint."""
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)
            self.validate_args(args)
            pre_tasks: List[TaskBase] = []
            filter_by_profile: Optional[FilterByProfile] = None
            trestle_root: pathlib.Path = pathlib.Path(args.working_dir)

            if args.filter_by_profile:
                filter_by_profile = FilterByProfile(
                    trestle_root, args.filter_by_profile
                )

            authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
                args.working_dir
            )
            authored_comp.create_new_default(
                args.profile_name,
                args.compdef_name,
                args.component_title,
                args.component_description,
                args.component_definition_type,
                filter_by_profile,
            )

            transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()

            # In this case we only want to do the transformation and generation for this component
            # definition, so we skip all other component definitions and components.
            model_filter: ModelFilter = ModelFilter(
                [], [args.compdef_name, args.component_title, f"{RULE_PREFIX}*"]
            )

            rule_transform_task: RuleTransformTask = RuleTransformTask(
                working_dir=args.working_dir,
                rules_view_dir=RULES_VIEW_DIR,
                rule_transformer=transformer,
                model_filter=model_filter,
            )
            pre_tasks.append(rule_transform_task)

            regenerate_task: RegenerateTask = RegenerateTask(
                authored_object=authored_comp,
                markdown_dir=args.markdown_path,
                model_filter=model_filter,
            )
            pre_tasks.append(regenerate_task)

            super().run_base(args, pre_tasks)
        except Exception as e:
            exit_code = handle_exception(e)

        sys.exit(exit_code)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Create new component definition with defaults."
    )
    set_default_component_fields = CreateCDEntrypoint(parser=parser)

    args = parser.parse_args()
    set_default_component_fields.run(args)


if __name__ == "__main__":
    main()

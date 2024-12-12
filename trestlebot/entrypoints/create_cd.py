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
import traceback
from typing import List, Optional

from ssg.products import (
    load_product_yaml,
    product_yaml_path
)

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
            required=True,
            help="Name of profile in the trestle workspace to use with the component definition.",
        )
        self.parser.add_argument(
            "--compdef-name", required=True, help="Name of component definition"
        )
        self.parser.add_argument(
            "--component-title", required=False, help="Title of initial component"
        )
        self.parser.add_argument(
            "--product-name",
            required=False,
            help="Name of the ComplainceAsCode content product.",
        )
        self.parser.add_argument(
            "--cac-path",
            required=False,
            help="Path of the ComplainceAsCode content path ",
        )
        self.parser.add_argument(
            "--component-description",
            required=True,
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

    def run(self, args: argparse.Namespace) -> None:
        """Run the entrypoint."""
        exit_code: int = SUCCESS_EXIT_CODE
        try:
            set_log_level_from_args(args)
            if not args.component_title:
                if not args.product_name or not args.cac_path:
                    raise ValueError(
                        "If --component-title is not provided, " +
                        "both --product-name and --cac-path must be provided."
                    )
            else:
                if args.product_name or args.cac_path:
                    raise ValueError(
                        "The --component-title is provided, no need --product-name and --cac-path."
                    )
            pre_tasks: List[TaskBase] = []
            filter_by_profile: Optional[FilterByProfile] = None
            trestle_root: pathlib.Path = pathlib.Path(args.working_dir)

            if args.filter_by_profile:
                filter_by_profile = FilterByProfile(
                    trestle_root, args.filter_by_profile
                )

            if args.component_title:
                component_title = args.component_title
            else:
                # Get the component title from SSG products
                component_title = self.get_product_title(
                    args.cac_path, args.product_name
                )

            authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
                args.working_dir
            )
            authored_comp.create_new_default(
                args.profile_name,
                args.compdef_name,
                component_title,
                args.component_description,
                args.component_definition_type,
                filter_by_profile,
            )

            transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()

            # In this case we only want to do the transformation and generation for this component
            # definition, so we skip all other component definitions and components.
            model_filter: ModelFilter = ModelFilter(
                [], [args.compdef_name, component_title, f"{RULE_PREFIX}*"]
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
            traceback_str = traceback.format_exc()
            exit_code = handle_exception(e, traceback_str)

        sys.exit(exit_code)

    def get_product_title(self, ssg_root, product_name: str) -> str:
        """Get the title of the product using the SSG products library."""
        try:
            # Get the product yaml file path
            product_yml_path = product_yaml_path(ssg_root, product_name)
            # Load the product data
            product = load_product_yaml(product_yml_path)
            # Return product name from product yml file
            return product._primary_data.get("product")
        except Exception as e:
            logger.error(f"Error retrieving product title: {e}", exc_info=True)


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

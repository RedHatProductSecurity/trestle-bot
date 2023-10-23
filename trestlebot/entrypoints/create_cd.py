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

"""
Entrypoint for component definition bootstrapping.

This will create a rules-view directory in the working directory, create a component
definition in JSON format with the initially generated rules and initial trestle control markdown.
"""

import argparse
import logging
from typing import List

from trestlebot.const import RULE_PREFIX, RULES_VIEW_DIR
from trestlebot.entrypoints.entrypoint_base import EntrypointBase
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.authored.types import AuthoredType
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
            "--component-title", required=True, help="Title of initial component"
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
            choices=["service", "validation"],
            default="service",
            help="Type of component definition",
        )

    def run(self, args: argparse.Namespace) -> None:
        """Run the entrypoint."""

        set_log_level_from_args(args)
        pre_tasks: List[TaskBase] = []

        # In this case we only want to do the transformation and generation for this component
        # definition, so we skip all other component definitions and components.
        filter: ModelFilter = ModelFilter(
            [], [args.compdef_name, args.component_title, f"{RULE_PREFIX}*"]
        )

        authored_comp = AuthoredComponentDefinition(args.working_dir)
        authored_comp.create_new_default(
            args.profile_name,
            args.compdef_name,
            args.component_title,
            args.component_description,
            args.component_definition_type,
        )

        transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()
        rule_transform_task: RuleTransformTask = RuleTransformTask(
            working_dir=args.working_dir,
            rules_view_dir=RULES_VIEW_DIR,
            rule_transformer=transformer,
            filter=filter,
        )
        pre_tasks.append(rule_transform_task)

        regenerate_task = RegenerateTask(
            working_dir=args.working_dir,
            authored_model=AuthoredType.COMPDEF.value,
            markdown_dir=args.markdown_path,
            filter=filter,
        )
        pre_tasks.append(regenerate_task)

        super().run_base(args, pre_tasks)


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

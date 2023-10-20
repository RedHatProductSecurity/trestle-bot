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

import argparse
from typing import List

from trestlebot.entrypoints.entrypoint_base import EntrypointBase, comma_sep_to_list
from trestlebot.entrypoints.log import set_log_level_from_args
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.regenerate_task import RegenerateTask
from trestlebot.tasks.rule_transform_task import RuleTransformTask
from trestlebot.transformers.yaml_transformer import ToRulesYAMLTransformer
from trestlebot.const import RULES_VIEW_DIR


class CreateCDEntrypoint(EntrypointBase):
    """Entrypoint for setting default component fields."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Initialize."""
        super().__init__(parser)
        self.setup_set_default_component_fields_arguments()

    def setup_set_default_component_fields_arguments(self) -> None:
        """Setup specific arguments for this entrypoint."""
        self.parser.add_argument(
            "--profile-name", required=True, help="Name of profile"
        )
        self.parser.add_argument(
            "--compdef-name", required=True, help="Name of component definition"
        )
        self.parser.add_argument(
            "--comp-title", required=True, help="Title of component"
        )
        self.parser.add_argument(
            "--comp-description", required=True, help="Description of component"
        )
        self.parser.add_argument(
            "--cd-type",
            required=False,
            default="service",
            help="Type of component definition",
        )
        self.parser.add_argument(
            "--generate",
            required=False,
            default=False,
            help="Generate markdown and ssp index",
        )
        self.parser.add_argument(
            "--transform-rules",
            required=False,
            default=False,
            help="Transform rules to YAML",
        )
            

    def run(self, args: argparse.Namespace) -> None:
        """Run the entrypoint."""
        set_log_level_from_args(args)
        authored_comp = AuthoredComponentDefinition(args.working_dir)
        authored_comp.create_new_default(
            args.profile_name,
            args.compdef_name,
            args.comp_title,
            args.comp_description,
            args.cd_type,
        )
        pre_tasks: List[TaskBase] = []
        if args.transform_rules:
            transformer: ToRulesYAMLTransformer = ToRulesYAMLTransformer()
            rule_transform_task: RuleTransformTask = RuleTransformTask(
                args.working_dir,
                args.RULES_VIEW_DIR,
                transformer,
                comma_sep_to_list(args.skip_items),
            )
            pre_tasks: List[TaskBase] = [rule_transform_task]
        if args.generate:
            regenerate_task = RegenerateTask(
                args.working_dir,
                "compdef",
                args.markdown_path,
                args.ssp_index_path,
                comma_sep_to_list(args.skip_items),
            )
            pre_tasks.append(regenerate_task)

        super().run_base(args, pre_tasks)


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Set default component fields entrypoint for trestle."
    )
    set_default_component_fields = CreateCDEntrypoint(parser=parser)

    args = parser.parse_args()
    set_default_component_fields.run(args)


if __name__ == "__main__":
    main()

#!/usr/bin/python

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.

"""
Find every action.yml file in the repo and README.md next to it
and update the Action Inputs and Action Outputs sections in the README.md
"""

import logging
import os
import sys
from typing import Any, List, Dict

from ruamel.yaml import YAML, YAMLError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ACTION_INPUTS_START = "<!-- START_ACTION_INPUTS -->"
ACTION_INPUTS_END = "<!-- END_ACTION_INPUTS -->"
ACTION_OUTPUTS_START = "<!-- START_ACTION_OUTPUTS -->"
ACTION_OUTPUTS_END = "<!-- END_ACTION_OUTPUTS -->"


class InvalidReadmeFile(Exception):
    """Exception raised for invalid README.md file"""

    def __init__(self, start_marker: str, end_marker: str) -> None:
        super().__init__(
            f"Missing start marker '{start_marker}' and/or "
            f"end marker '{end_marker}' in README.md file"
        )


def load_action_yml(action_yml_file: str) -> Dict[str, Any]:
    """Load the action.yml file as a dictionary"""
    with open(action_yml_file, "r") as stream:
        try:
            yaml = YAML(typ="safe")
            action_yml = yaml.load(stream)
        except YAMLError as e:
            raise RuntimeError(f"Error loading YAML file '{action_yml_file}': {e}")
    return action_yml


def generate_inputs_markdown_table(inputs: Dict[str, Any]) -> str:
    """Generate the Action Inputs markdown table"""
    table = "| Name | Description | Default | Required |\n| --- | --- | --- | --- |\n"
    for name, input in inputs.items():
        table += f"| {name} | {input.get('description', None)} | {input.get('default', None)} | {input.get('required', None)} |\n"  # noqa E501
    return table


def generate_outputs_markdown_table(outputs: Dict[str, Any]) -> str:
    """Generate the Action Outputs markdown table"""
    table = "| Name | Description |\n| --- | --- |\n"
    for name, output in outputs.items():
        table += f"| {name} | {output.get('description', None)} |\n"
    return table


def replace(all_content: str, start: str, end: str, new_content: str) -> str:
    """Replace the content between start (plus a new line) and end with new_content"""
    start_line = all_content.find(start)
    end_line = all_content.find(end)
    if start_line == -1 or end_line == -1:
        raise InvalidReadmeFile(start, end)

    lines: List[str] = all_content.split("\n")

    start_marker_index = lines.index(start)
    end_marker_index = lines.index(end)

    # Replace content between markers excluding marker lines
    lines = lines[: start_marker_index + 1] + [new_content] + lines[end_marker_index:]
    updated_content = "\n".join(lines)
    return updated_content


def replace_readme_sections(content: str, action_yml: Dict[str, Any]) -> str:
    """Replace the Action Inputs and Action Outputs sections in the README.md file"""
    inputs_table = generate_inputs_markdown_table(action_yml["inputs"])
    outputs_table = generate_outputs_markdown_table(action_yml["outputs"])
    replaced_content = replace(
        content, ACTION_INPUTS_START, ACTION_INPUTS_END, inputs_table
    )
    replaced_content = replace(
        replaced_content, ACTION_OUTPUTS_START, ACTION_OUTPUTS_END, outputs_table
    )
    return replaced_content


def update_readme_file(readme_file: str, action_yml: Dict[str, Any]) -> None:
    """Updates the README.md file with action inputs and outputs"""
    with open(readme_file, "r") as stream:
        existing_content = stream.read()
        try:
            updated_content = replace_readme_sections(existing_content, action_yml)
        except InvalidReadmeFile as e:
            logging.warning(f"Skipping README file {readme_file}: {e}")
            return  # Don't continue if the readme file is invalid

    if updated_content != existing_content:
        logging.info(f"Updated README.md file: {readme_file}")
        with open(readme_file, "w") as stream:
            stream.write(updated_content)
    else:
        logging.info(f"README.md file is up to date: {readme_file}")


def find_actions_files() -> List[str]:
    """Find every action.yml file in the repo"""
    action_yml_files: List[str] = []
    for root, _, files in os.walk("actions"):
        for file in files:
            if file.endswith("action.yml"):
                action_yml_files.append(os.path.join(root, file))
    return action_yml_files


def main() -> None:
    try:
        action_yml_files: List[str] = find_actions_files()
        for action_yml_file in action_yml_files:
            # find the README.md file next to the action.yml file
            readme_file = action_yml_file.replace("action.yml", "README.md")
            if not os.path.exists(readme_file):
                logging.warning(
                    f"README.md not found for action.yml file: {action_yml_file}"
                )
                continue

            action_yml: Dict[str, Any] = load_action_yml(action_yml_file)
            update_readme_file(readme_file, action_yml)
    except Exception as e:
        logging.exception(f"Unexpected error during README.md updates: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

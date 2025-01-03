# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

import datetime
import json
from pathlib import Path

from ssg.products import load_product_yaml, product_yaml_path


def get_component_title(product_name: str, cac_path: str) -> str:
    """Get the product name from product yml file via the SSG library."""
    if product_name and cac_path:
        # Get the product yaml file path
        product_yml_path = product_yaml_path(cac_path, product_name)
        # Load the product data
        product = load_product_yaml(product_yml_path)
        # Return product name from product yml file
        return product._primary_data.get("product")
    else:
        raise ValueError("component_title is empty or None")


def update_component_definition(compdef_file: Path) -> None:
    # Update the component definition version and modify time
    with open(compdef_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    current_version = data["component-definition"]["metadata"]["version"]
    data["component-definition"]["metadata"]["version"] = str(
        "{:.1f}".format(float(current_version) + 0.1)
    )
    current_time = datetime.datetime.now().isoformat()
    data["component-definition"]["metadata"]["last-modified"] = current_time
    with open(compdef_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

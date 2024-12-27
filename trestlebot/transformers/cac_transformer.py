# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Cac content Transformer for rule authoring. """

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

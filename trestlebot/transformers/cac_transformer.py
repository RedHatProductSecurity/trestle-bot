# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Transform rules from existing Compliance as Code locations into OSCAL properties."""


from typing import Dict, List, Tuple

import ssg.products


def get_component_info(product_name: str, cac_path: str) -> Tuple[str, str]:
    """Get the product name from product yml file via the SSG library."""
    if product_name and cac_path:
        # Get the product yaml file path
        product_yml_path = ssg.products.product_yaml_path(cac_path, product_name)
        # Load the product data
        product = ssg.products.load_product_yaml(product_yml_path)
        # Return product name from product yml file
        component_title = product._primary_data.get("product")
        component_description = product._primary_data.get("full_name")
        return (component_title, component_description)
    else:
        raise ValueError("component_title is empty or None")


def get_validation_component_mapping(
    props: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Adds a new "Check_Id" and "Check_Description" to the props based on the
    "Rule_Id" value and "Rule_Description".

    Args:
        props (List[Dict]): The input list of dictionaries.

    Returns:
        List[Dict]: The updated list with the new "Check_Id" and
        "Check_Description" entry.
    """

    props = props
    rule_check_mapping = []
    check_id_entry = {}
    for prop in props:
        if prop["name"] == "Rule_Id":
            rule_check_mapping.append(prop)
            check_id_entry = {
                "name": "Check_Id",
                "ns": prop["ns"],
                "value": prop["value"],
                "remarks": prop["remarks"],
            }
        if prop["name"] == "Rule_Description":
            rule_check_mapping.append(prop)
            rule_check_mapping.append(check_id_entry)
            check_description_entry = {
                "name": "Check_Description",
                "ns": prop["ns"],
                "value": prop["value"],
                "remarks": prop["remarks"],
            }
            rule_check_mapping.append(check_description_entry)
    return rule_check_mapping

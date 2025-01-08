# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Transform rules from existing Compliance as Code locations into OSCAL properties."""

import json
import logging
import os
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

import ssg.build_yaml
import ssg.products
import ssg.rules
from ssg.utils import required_key
from trestle.common.const import TRESTLE_GENERIC_NS
from trestle.core.generators import generate_sample_model
from trestle.oscal.common import Property
from trestle.tasks.csv_to_oscal_cd import RULE_DESCRIPTION, RULE_ID, _RuleSetIdMgr


logger = logging.getLogger(__name__)

XCCDF_VARIABLE = "xccdf_variable"
TRESTLE_CD_NS = f"{TRESTLE_GENERIC_NS}/cd"


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


def add_prop(name: str, value: str, remarks: Optional[str] = None) -> Property:
    """Add a property to a set of rule properties."""
    prop = generate_sample_model(Property)
    prop.name = name
    prop.value = value
    if remarks:
        prop.remarks = remarks
    prop.ns = TRESTLE_CD_NS  # type: ignore
    return prop


def get_benchmark_root(root: str, product: str) -> str:
    """Get the benchmark root."""
    product_yaml_path = ssg.products.product_yaml_path(root, product)
    product_yaml = ssg.products.load_product_yaml(product_yaml_path)
    product_dir = product_yaml.get("product_dir")
    benchmark_root = os.path.join(product_dir, product_yaml.get("benchmark_root"))
    return benchmark_root


class RuleInfo:
    """Stores rule information."""

    def __init__(self, rule_id: str, rule_dir: str) -> None:
        """Initialize."""
        self._id = rule_id
        self._description = ""
        self._rule_dir = rule_dir

    @property
    def id(self) -> str:
        """Get the id."""
        return self._id

    @property
    def description(self) -> str:
        """Get the description."""
        return self._description

    @property
    def rule_dir(self) -> str:
        """Get the rule directory."""
        return self._rule_dir

    def add_description(self, value: str) -> None:
        """Add a rule description."""
        self._description = value


class RulesTransformer:
    """Transforms rules into properties for creating component definitions."""

    def __init__(
        self,
        root: str,
        env_yaml: Dict[str, Any],
        rule_dirs_json_path: str,
    ) -> None:
        """Initialize."""
        with open(rule_dirs_json_path, "r") as f:
            rule_dir_json = json.load(f)
        self.rule_json = rule_dir_json
        self.root = root
        self.env_yaml = env_yaml
        self.product = required_key(env_yaml, "product")

        benchmark_root = get_benchmark_root(root, self.product)
        self.rules_dirs_for_product: Dict[str, str] = dict()
        for dir_path in ssg.rules.find_rule_dirs_in_paths([benchmark_root]):
            rule_id = ssg.rules.get_rule_dir_id(dir_path)
            self.rules_dirs_for_product[rule_id] = dir_path

        self._rules_by_id: Dict[str, RuleInfo] = dict()

    def add_rules(self, rules: List[str]) -> None:
        """
        Load a set of rules into rule objects based on ids and
        add them to the rules_by_id dictionary.

        Args:
            rules: A list of rule ids.

        Notes: This attempt to load all rules and will raise an error if any fail.
        """
        rule_errors: List[str] = list()

        for rule_id in rules:
            error = self.add_rule(rule_id)
            if error:
                rule_errors.append(error)

        if len(rule_errors) > 0:
            raise RuntimeError(
                f"Error loading rules: \
                    \n{', '.join(rule_errors)}"
            )

    def add_rule(self, rule_id: str) -> Optional[str]:
        """Add a single rule to the rules_by_id dictionary."""
        try:
            if rule_id not in self._rules_by_id:
                rule_obj = self._new_rule_obj(rule_id)
                self._load_rule_yaml(rule_obj)
                self._rules_by_id[rule_id] = rule_obj
        except ValueError as e:
            return f"Could not find rule {rule_id}: {e}"
        except FileNotFoundError as e:
            return f"Could not load rule {rule_id}: {e}"
        return None

    def _new_rule_obj(self, rule_id: str) -> RuleInfo:
        """Create a new rule object."""
        rule_dir = self._from_rules_json(rule_id)
        if not rule_dir:
            rule_dir = self._from_product_dir(rule_id)
        if not rule_dir:
            raise ValueError(
                f"Could not find rule {rule_id} in rules json or product directory."
            )
        rule_obj = RuleInfo(rule_id, rule_dir)
        return rule_obj

    def _from_rules_json(self, rule_id: str) -> Optional[str]:
        """Locate the rule dir in the rule JSON."""
        if rule_id not in self.rule_json:
            return None
        return self.rule_json[rule_id]["dir"]

    def _from_product_dir(self, rule_id: str) -> Optional[str]:
        """Locate the rule dir in the product directory."""
        if rule_id not in self.rules_dirs_for_product:
            return None
        return self.rules_dirs_for_product.get(rule_id)

    def _load_rule_yaml(self, rule_obj: RuleInfo) -> None:
        """
        Update the rule object with the rule yaml data.

        Args:
            rule_obj: The rule object where collection rule data is stored.
        """
        rule_file = ssg.rules.get_rule_dir_yaml(rule_obj.rule_dir)
        rule_yaml = ssg.build_yaml.Rule.from_yaml(rule_file, env_yaml=self.env_yaml)
        rule_yaml.normalize(self.product)
        description = self._clean_rule_description(rule_yaml.description)
        rule_obj.add_description(description)

    @staticmethod
    def _clean_rule_description(description: str) -> str:
        """Clean the rule description."""
        parser = HTMLParser()
        parser.handle_data(description)
        cleaned_description = description.replace("\n", " ").strip()
        cleaned_description = re.sub(" +", " ", cleaned_description)
        return cleaned_description

    def _get_rule_properties(self, ruleset: str, rule_obj: RuleInfo) -> List[Property]:
        """Get a set of rule properties for a rule object."""
        rule_properties: List[Property] = list()

        # Add rule properties for the rule set
        rule_properties.append(add_prop(RULE_ID, rule_obj.id, ruleset))
        rule_properties.append(
            add_prop(RULE_DESCRIPTION, rule_obj.description, ruleset)
        )

        return rule_properties

    def get_rule_id_props(self, rule_ids: List[str]) -> List[Property]:
        """
        Get the rule id property for a rule id.

        Note:
            This is used for linking rules to rulesets. Not the rules must be loaded
            with add_rules before calling this method.
        """
        props: List[Property] = list()
        for rule_id in rule_ids:
            if rule_id not in self._rules_by_id:
                raise ValueError(f"Could not find rule {rule_id}")
            props.append(add_prop(RULE_ID, rule_id))
        return props

    def get_all_rules(self) -> List[RuleInfo]:
        """Get all rules that have been loaded"""
        return list(self._rules_by_id.values())

    def transform(self, rule_objs: List[RuleInfo]) -> List[Property]:
        """Get the rules properties for a set of rule ids."""
        rule_properties: List[Property] = list()

        start_val = -1
        for i, rule_obj in enumerate(rule_objs):
            rule_set_mgr = _RuleSetIdMgr(start_val + i, len(rule_objs))
            rule_set_props = self._get_rule_properties(
                rule_set_mgr.get_next_rule_set_id(), rule_obj
            )
            rule_properties.extend(rule_set_props)
        return rule_properties

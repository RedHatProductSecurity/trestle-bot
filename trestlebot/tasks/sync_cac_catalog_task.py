# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import logging
import os
import pathlib
from typing import List

from pydantic.v1.typing import is_callable_type
from ssg.controls import ControlsManager, Policy
# from ssg.products import get_all
from ssg.profiles import get_profiles_from_products
from trestle.common.list_utils import none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.generators import generate_sample_model
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.common import Property, Parameter
from trestle.oscal.component import ComponentDefinition, DefinedComponent
from trestle.oscal.catalog import Catalog, Control, Group

from trestlebot import const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    RuleInfo,
    RulesTransformer,
    get_component_info,
    get_validation_component_mapping,
)


logger = logging.getLogger(__name__)


class SyncCacCatalogTask(TaskBase):
    """Sync CaC policy controls to OSCAL catalog task."""
    cac_content_root: pathlib.Path
    cac_control: str
    oscal_catalog: str

    def __init__(
        self,
        cac_content_root: pathlib.Path,
        cac_control: str,
        oscal_catalog: str,
        working_dir: str,
    ) -> None:
        """Initialize CaC catalog sync task."""
        super().__init__(working_dir, None)
        self.cac_content_root = cac_content_root
        self.cac_control = cac_control # example: nist_rev5_800_53
        self.oscal_catalog = oscal_catalog
        self.rules: List[str] = []


    def _load_policy_controls(self) -> Policy:
        controls_dir = self.cac_content_root / "controls"
        policy_yaml = controls_dir / f"{self.cac_control}.yml"
        if not policy_yaml.exists():
            raise Exception(f"Policy {policy_yaml} does not exist")

        policy = Policy(policy_yaml)
        policy.load()
        return policy
        # Old approach: use ControlsManager to load all policies (fails to load some policies)
        # New approach: load single Policy file
        # controls_manager = ControlsManager(controls_dir.resolve().as_posix())
        # controls_manager.policies

    def _add_props(self, oscal_catalog: Catalog) -> Catalog:
        """Add base props to OSCAL catalog."""
        oscal_catalog.metadata.title = "openscap"
        return oscal_catalog

    def _update_catalog(
            self,
            catalog_json: pathlib.Path,
            oscal_catalog: Catalog,
            policy: Policy,
    ) -> None:
        """Update existed OSCAL component definition."""
        catalog = Catalog.oscal_read(catalog_json)
        updated = False
        # for index, component in enumerate(catalog.components):
        #     components_titles.append(component.title)
        #     # If the component exists and the props need to be updated
        #     if component.title == oscal_catalog.title:
        #         if component.props != oscal_catalog.props:
        #             logger.info(f"Start to update props of {component.title}")
        #             catalog.components[index].props = oscal_catalog.props
        #             updated = True
        #             catalog.oscal_write(catalog_json)
        #             break
        #
        # if oscal_catalog.title not in components_titles:
        #     logger.info(f"Start to append component {oscal_catalog.title}")
        #     catalog.components.append(oscal_catalog)
        #     catalog.oscal_write(catalog_json)
        #     updated = True
        #
        if updated:
            logger.info(f"Updated catalog: {catalog_json}")
            catalog.metadata.version = str(
                "{:.1f}".format(float(catalog.metadata.version) + 0.1)
            )
            ModelUtils.update_last_modified(catalog)
            catalog.oscal_write(catalog_json)

    def _create_catalog(
            self,
            catalog_json: pathlib.Path,
            catalog_base: Catalog,
            policy: Policy,
            # params: list[Parameter],
            # controls: list[Control],
            # groups: list[Group],
    ) -> None:
        """Create a component definition in OSCAL."""
        oscal_catalog = generate_sample_model(Catalog)
        oscal_catalog.metadata.title = f"Catalog for {self.cac_control}"
        oscal_catalog.metadata.version = "1.0"
        oscal_catalog.params = []
        oscal_catalog.controls = []
        oscal_catalog.groups = []
        oscal_catalog.back_matter = None
        catalog_dir = pathlib.Path(os.path.dirname(catalog_json))
        catalog_dir.mkdir(exist_ok=True, parents=True)
        oscal_catalog.oscal_write(catalog_json)

    def _create_or_update_catalog(self, policy: Policy) -> None:
        """Create or update catalog for specified CaC profile."""
        oscal_catalog_base: Catalog = generate_sample_model(Catalog)
        oscal_catalog_base = self._add_props(oscal_catalog_base)
        repo_path = pathlib.Path(self.working_dir)
        oscal_json = ModelUtils.get_model_path_for_name_and_class(
            repo_path,
            self.cac_control,
            Catalog,
            FileContentType.JSON,
        )
        if oscal_json.exists():
            logger.info(f"The catalog for {self.cac_control} exists.")
            self._update_catalog(oscal_json, oscal_catalog_base, policy)
        else:
            logger.info(f"Creating catalog {self.cac_control}")
            self._create_catalog(oscal_json, oscal_catalog_base, policy)

    def execute(self) -> int:
        """Execute task to create or update product component definition."""
        policy = self._load_policy_controls()
        self._create_or_update_catalog(policy)
        return const.SUCCESS_EXIT_CODE

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Trestle Bot Sync CaC Content Tasks"""

import logging
import os
import pathlib
import re
from typing import List

import ssg
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
from trestle.oscal import common
from trestle.common import const

from trestlebot import const
from trestlebot.tasks.base_task import TaskBase
from trestlebot.transformers.cac_transformer import (
    RuleInfo,
    RulesTransformer,
    get_component_info,
    get_validation_component_mapping,
)


logger = logging.getLogger(__name__)



def get_oscal_control_title(
        cac_control_id: str,
        cac_control_title: str | None,
        parent_title: str | None
):
    if not cac_control_title:
        # logger.warn()
        return cac_control_id
    title = cac_control_title.removeprefix(cac_control_id)
    title = re.sub(r"^\W*", "", title)
    if parent_title:
        group, _, section = title.partition("|")
        group = group.strip()
        if group.lower() in parent_title.lower():
            title = section
            title = title.strip()
    title = re.sub(r"^\W*", "", title)
    title = title.title()
    return title


def control_cac_to_oscal(
        cac_control: ssg.controls.Control,
        group_id: str,
        oscal_path: List[str],
        parent: Control | Group | None = None
) -> Control:
    # 1. Create control and populate basics
    oscal_control = generate_sample_model(Control)
    control_id_str = ".".join(oscal_path)
    cac_control_id = f"{group_id}-{control_id_str}"
    oscal_control.id = cac_control_id
    oscal_control.class_ = 'CAC_IMPORT'
    oscal_title = get_oscal_control_title(cac_control.id, cac_control.title, parent.title)
    oscal_control.title = oscal_title
    oscal_control.props = []
    oscal_control.params = []
    oscal_control.parts = []
    sort_control_path = ".".join(part.zfill(2) for part in oscal_path)
    sort_id = f"{group_id}-{sort_control_path}"
    oscal_control.props.append(common.Property(name=const.LABEL, value=cac_control_id))
    oscal_control.props.append(common.Property(name=const.SORT_ID, value=sort_id))

    # 2. Populate params
    if cac_control.description:
        assignments = re.findall(r"\[Assignment: (.*?)]", cac_control.description) or []
        assignment_ids = []
        for param_n, assignment in enumerate(assignments, 1):
            assignment_ids.append(f"{cac_control_id}_prm_{param_n}")
        for assignment_id, assignment in zip(assignment_ids, assignments):
            oscal_control.params.append(common.Parameter(id=assignment_id, label=assignment))
        statement = re.search(r"(.*)$", cac_control.description, re.MULTILINE)
        if statement:
            statement_text = statement.group(1)
            for assignment_id, assignment in zip(assignment_ids, assignments):
                statement_text = statement_text.replace(assignment, " {{ insert: param, " + assignment_id + " }} ")
                statement_text = statement_text.replace(f"{cac_control_id}_prm_{assignment_id}", "")
            oscal_control.parts.append(common.Part(id=f"{cac_control_id}_smt", name=const.STATEMENT))

        guidance = re.search(r"^(?:Supplemental )?Guidance: (.*?)$", cac_control.description, re.MULTILINE)
        if guidance:
            # TODO: add guidance const to trestle
            oscal_control.parts.append(common.Part(id=f"{cac_control_id}_gdn", name="guidance", prose=guidance.group(1)))
    return oscal_control


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
    ) -> None:
        """Create a component definition in OSCAL."""
        oscal_catalog = generate_sample_model(Catalog)
        oscal_catalog.metadata.title = f"Catalog for {self.cac_control}"
        for cac_control in policy.controls:
            # 1. extract oscal-compatible identifiers
            group_id, *control_path = [x.lower() for x in re.findall(r"\w+", cac_control.id)]
            # 2. find the correct place in oscal
            # 2a. find the group
            group = None
            for g in oscal_catalog.groups:
                if g.id == group_id:
                    group = g
                    break
            # 2b. If the group doesn't exist, create it
            if not group:
                group = generate_sample_model(Group)
                group.id = group_id
                oscal_catalog.groups.append(group)
            if not group.controls:
                group.controls = []
            parent = group
            # 3. If this is a nested control, get the parent control
            is_nested_control = len(control_path) > 1
            if is_nested_control:
                # search the controls for the next path until the last path part
                for parent_path_len in range(1, len(control_path)):
                    parent_id = f"{group_id}-{'.'.join(control_path[:parent_path_len])}"
                    found = False
                    for control in parent.controls:
                        if control.id == parent_id:
                            if not control.controls:
                                control.controls = []
                            parent = control
                            found = True
                            break
                    if not found:
                        raise ValueError("Nested control path before parent control definition")
            # 4. Map the cac control to the oscal control
            control = control_cac_to_oscal(cac_control, group_id, control_path, parent)
            # 5. Add the control to the group
            parent.controls.append(control)

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

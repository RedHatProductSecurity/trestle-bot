# Current work for sync_cac_content_profile
# Task to leverage ComplianceasCode/content ControlsManager
# Interaction with CLI
import logging
import os
from typing import Any, Dict, List

from ssg.controls import ControlsManager
from ssg.products import (
    get_profile_files_from_root,
    load_product_yaml,
    product_yaml_path,
)

from trestlebot import const
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.base_task import TaskBase, TaskException


logger = logging.getLogger(__name__)


class SyncCacContentProfileTask(TaskBase):
    def __init__(
        self,
        cac_content_root: str,
        product: str,
        oscal_catalog: str,
        policy_id: str,
        filter_by_level: List[str],
        authored_profile: AuthoredProfile,
    ):
        self.cac_content_root = cac_content_root
        self.product = product
        self.oscal_catalog = oscal_catalog
        self.policy_id = policy_id
        self.filter_by_level = filter_by_level
        self.authored_profile = authored_profile
        working_dir = self.authored_profile.get_trestle_root()
        super().__init__(working_dir=working_dir, model_filter=None)

    def get_control_ids_by_level(self, policy_id: str, filter_by_level: str) -> None:
        """
        Collecting control file product data
        """

        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)

        control_manager = ControlsManager(
            os.path.join(self.cac_content_root, "controls"), product_data
        )

        control_manager.load()
        # accessing control file within content/controls
        # the instance can use the methods within the ControlsManager() class

        # TODO Ask Marcus to address use of get_policy in PR notes
        default_levels = control_manager.get_all_controls(policy_id)
        extract_policy = control_manager._get_policy(policy_id)
        logger.debug(
            f"Organizing controls based on {filter_by_level}. If no level is specified, all controls will be organized."
        )
        if not filter_by_level:
            all_controls = control_manager.get_all_controls(policy_id)
            self.create_oscal_profile(all_controls)
            logger.debug(
                f"No level indicated. Sorting based on {policy_id} default levels."
            )
        else:
            for level in filter_by_level:
                eligible_controls = control_manager.get_all_controls_of_level(level)
                self.create_oscal_profile(eligible_controls)
                # make oscal profile
                logger.debug(f"Creating oscal profile using {eligible_controls}.")
                # if filter_by_profile = "high" filter_by_profile.upper()
                # when making new json -> profile-HIGH.json

    def create_oscal_profile(
        self,
        import_path: str,
        controls: List[str],
        name_update: str,
    ) -> None:
        # Step 1: If filter by level returns eligible controls, create OSCAL profile with suffix change based on level
        # Step 2: Fill in with control id, loading from eligible controls and all controls
        self.import_path = import_path
        self.controls = controls
        # catalog is import_path
        self.name_update = name_update
        name_update = f"{self.policy_id}-{self.filter_by_level}.json"
        # If the import_path is not valid then create new default (based on tasks/authored/profile.py)
        # Otherwise the existing copy is held as a deep copy and will be accessible even if changing profile inputs
        # Checks for importing model types (catalog, baseline)
        # AuthoredProfile will update based on existing_import
        # If the models aren't equivalent based on the deep copy of the existing profile
        # Then modelUtils will update profile element that was recently updated and write to the profile_path
        self.authored_profile.create_new_default(controls, name_update)

    def execute(self) -> int:
        # calling to get_control_ids _by_level and checking for valid control file name
        try:
            self.get_control_ids_by_level(
                policy_id=self.policy_id, filter_by_level=self.filter_by_level
            )
        except KeyError as e:
            raise TaskException(
                f"The control file associated with {self.policy_id} does not exist."
            ) from e
        return const.SUCCESS_EXIT_CODE

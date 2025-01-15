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
        """
        Initializes the SyncCacContentProfileTask.

        Args:
            cac_content_root (str): The root directory of the CAC content repository that will access specified policy ids.
            product (str): The product name for the CAC content repository and Oscal Profile.
            oscal_catalog (str): The catalog used for extracting policy ids and Profile data.
            policy_id (str): The control file that includes control ids and their associated levels to create OSCAL Profiles.
            filter_by_level (list): The optional flag indicating a specific level to filter controls in policy ids.
            authored_profile (AuthoredProfile): Task that leverages oscal to author OSCAL Profiles in trestle-bot.

        """
        self.cac_content_root = cac_content_root
        self.product = product
        self.oscal_catalog = oscal_catalog
        self.policy_id = policy_id
        self.filter_by_level = filter_by_level
        self.authored_profile = authored_profile
        working_dir = self.authored_profile.get_trestle_root()
        super().__init__(working_dir=working_dir, model_filter=None)

    def get_control_ids_by_level(
        self, policy_id: str, filter_by_level: List[str]
    ) -> None:
        """
        Collecting control file product data by input of policy id and optional filter by level.
        This method gets default levels based on policy id and updates based on `filter_by_level`.
        The optional `filter_by_level` will be leveraged to produce OSCAL Profile for desired baseline level.

        Args:
            policy_id (str): Policy ID for sourcing control file.
            filter_by_level: List[str]: User indicated baseline level that will be used to filter control files.

        """

        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)

        control_manager = ControlsManager(
            os.path.join(self.cac_content_root, "controls"), product_data
        )

        control_manager.load()

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

    def create_oscal_profile(
        self,
        import_path: str,
        controls: List[str],
        name_update: str,
    ) -> None:
        """
        Args:
            import_path (str): The supplied catalog or profile to use for authoring OSCAL Profiles.
            controls (List[str]): List of controls to include in the profile based on level handling.
            name_update (str): Name update to use based on filter_by_level user input
        Returns:
            None. Follows through by using AuthoredProfile task to create or update OSCAL Profiles.
        """
        # Step 1: If filter by level returns eligible controls, create OSCAL profile with suffix change based on level
        # Step 2: Fill in with control id, loading from eligible controls and all controls
        self.import_path = import_path
        self.controls = controls
        self.name_update = name_update

        name_update = f"{self.policy_id}-{self.filter_by_level}.json"
        self.authored_profile.create_or_update(import_path, name_update, controls)

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

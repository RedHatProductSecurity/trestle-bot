# import os
# from typing import Any, Dict, List
#
# from ssg.controls import ControlsManager
# from ssg.entities.profile import ProfileWIthInlinePolicies
#
# from trestlebot.tasks.authored.base_authored import AuthoredObjectBase
# from trestlebot.tasks.base_task import TaskBase
#
#
# class SyncCacContentProfileTask(TaskBase):
#     """
#     Sync CaC content to OSCAL profile task.
#     """
#
#     def __init__(
#         self,
#         product: str,
#         cac_profile: str,
#         cac_content_root: str,
#         compdef_type: str,
#         oscal_profile: str,
#         authored_object: AuthoredObjectBase,
#     ) -> None:
#         self.product: str = product
#         self.cac_profile: str = cac_profile
#         self.cac_content_root: str = cac_content_root
#         self.compdef_type: str = compdef_type
#         self.rules_json_path: str = ""
#         self.env_yaml: Dict[str, Any] = {}
#         self.selected: List[str] = []
#         self._authored_object = authored_object
#         self.filter_by_level = filter_by_level
#         working_dir = self._authored_object.get_trestle_root()
#         super().__init__(working_dir, None)

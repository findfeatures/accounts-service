import logging

from accounts import utils
from accounts.service.base import ServiceMixin
from nameko.rpc import rpc


logger = logging.getLogger(__name__)


class ProjectsServiceMixin(ServiceMixin):
    @rpc
    @utils.log_entrypoint
    def get_verified_projects(self, user_id):
        # verified because the user hasn't accepted the invitation yet!
        projects = self.storage.projects.get_all_verified(user_id)

        return [
            {
                "id": project["id"],
                "name": project["name"],
                "created_datetime_utc": project["created_datetime_utc"].isoformat(),
            }
            for project in projects
        ]

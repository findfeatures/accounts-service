import logging

from accounts import utils
from accounts.service.base import ServiceMixin
from nameko.rpc import rpc
from accounts.dependencies.database.collections.audit_logs import AuditLogType

logger = logging.getLogger(__name__)


class ProjectsServiceMixin(ServiceMixin):
    @rpc
    @utils.log_entrypoint
    def create_project(self, user_id, name):
        project_id = self.storage.projects.create_project(user_id, name)

        create_project_audit_log = AuditLogType.create_project(name, user_id)

        self.storage.audit_logs.create_log(
            project_id,
            create_project_audit_log.log_type,
            create_project_audit_log.meta_data,
        )
        return project_id

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

    @rpc
    @utils.log_entrypoint
    def is_project_ready(self, user_id, stripe_session_id):
        projects = self.storage.projects.get_all_verified(user_id)

        for project in projects:
            if project["checkout_session_id"] == stripe_session_id:
                return True

        return False

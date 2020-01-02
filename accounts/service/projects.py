import logging
from uuid import uuid4

from accounts import schemas, utils
from accounts.service.base import ServiceMixin
from accounts.utils import generate_token
from nameko.rpc import rpc
from sqlalchemy import exc


logger = logging.getLogger(__name__)


class ProjectsServiceMixin(ServiceMixin):
    pass
    # @rpc(expected_exceptions=(None,))
    # @utils.log_entrypoint
    # def create_user(self, project_details):
    #     project_details = schemas.CreateProjectRequest().load(project_details)
    #
    #     try:
    #         project_id = self.storage.projects.create(project_details["name"])
    #         return project_id
    #     except exc.IntegrityError:
    #         raise UserAlreadyExists(f'email {user_details["email"]} already exists')

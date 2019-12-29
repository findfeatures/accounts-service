import logging

import jwt
from nameko import config
from nameko.rpc import rpc
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from users import schemas, utils
from users.exceptions import UserAlreadyExists, UserDoesNotExist, UserNotAuthorised
from users.service.base import ServiceMixin

logger = logging.getLogger(__name__)


class UsersServiceMixin(ServiceMixin):

    @rpc(expected_exceptions=(UserDoesNotExist,))
    @utils.log_entrypoint
    def get_user(self, user_id):
        try:
            user_details = self.storage.users.get(user_id)

            created_datetime_utc = user_details["created_datetime_utc"].isoformat()

            user_details["created_datetime_utc"] = created_datetime_utc

            if user_details["deleted_datetime_utc"]:
                user_details["deleted_datetime_utc"] = user_details[
                    "deleted_datetime_utc"
                ].isoformat()

            return user_details
        except orm_exc.NoResultFound:
            raise UserDoesNotExist(f"User with id {user_id} does not exist")

    @rpc(expected_exceptions=(UserAlreadyExists,))
    @utils.log_entrypoint
    def create_user(self, user_details):
        user_details = schemas.CreateUserRequest().load(user_details)

        try:
            user_id = self.storage.users.create(
                user_details["email"],
                user_details["password"],
                user_details["display_name"],
            )
            return user_id
        except exc.IntegrityError:
            raise UserAlreadyExists(f'email {user_details["email"]} already exists')

    @rpc(expected_exceptions=(UserDoesNotExist,))
    @utils.log_entrypoint
    def delete_user(self, user_id):
        try:
            self.storage.users.delete(user_id)
        except orm_exc.NoResultFound as e:
            raise UserDoesNotExist(f"user_id {user_id} does not exist")

    @rpc(expected_exceptions=(UserNotAuthorised,))
    @utils.log_entrypoint
    def auth_user(self, email, password):
        is_correct_password = self.storage.users.is_correct_password(email, password)

        if not is_correct_password:
            raise UserNotAuthorised("user not authorised for this request")

        # not the most ideal code but i want to keep the
        # requests here to storage quite easy to test
        # and maintain
        user_details = self.storage.users.get_from_email(email)

        jwt_result = {
            "JWT": jwt.encode(
                {"user_id": user_details["id"], "email": user_details["email"]},
                config.get("JWT_SECRET"),
                algorithm="HS256",
            ).decode("utf-8")
        }

        return jwt_result

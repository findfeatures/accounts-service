import datetime

from ddtrace import Pin
from nameko import config
from nameko_sqlalchemy import Database
from sqlalchemy.orm import exc as orm_exc
from users import utils
from users.dependencies.database.models import Base, User, UserToken


class Collection:
    name = None
    model = None

    def __init__(self, db):
        self.db = db


class Users(Collection):
    name = "users"
    model = User

    @utils.sa_to_dict(sensitive_fields=["password"])
    def get(self, user_id):

        user = self.db.session.query(self.model).get(user_id)

        if not user:
            raise orm_exc.NoResultFound(f"No user with id {user_id} found")

        return user

    @utils.sa_to_dict(sensitive_fields=["password"])
    def get_from_email(self, email):

        user = self.db.session.query(self.model).filter_by(email=email).one_or_none()

        if not user:
            raise orm_exc.NoResultFound(f"No user with email {email} found")

        return user

    def create(self, email, password, display_name):
        new_user = self.model(email=email, password=password, display_name=display_name)
        with self.db.get_session() as session:
            session.add(new_user)
        return new_user.id

    def delete(self, user_id):
        with self.db.get_session() as session:
            user = session.query(self.model).filter_by(id=user_id).one()
            user.deleted_datetime_utc = datetime.datetime.utcnow()

    def is_correct_password(self, email, password):
        user = self.db.session.query(self.model).filter_by(email=email).one_or_none()

        if not user or user.deleted_datetime_utc is not None:
            return False

        return user.password == password


class UserTokens(Collection):
    name = "user_tokens"
    model = UserToken

    def create(self, user_id, token):
        new_token = self.model(user_id=user_id, token=token)

        with self.db.get_session() as session:
            session.add(new_token)


class StorageWrapper:
    def __init__(self, db, collections):
        self.db = db
        self.collections = collections
        self.register_collections()

    def register_collections(self):
        for collection in self.collections:
            setattr(self, collection.name, collection(self.db))

    def health_check(self):
        self.db.session.execute("SELECT 1 FROM users LIMIT 1")


class Storage(Database):
    collections = [Users, UserTokens]

    def __init__(self):
        engine_options = {
            "pool_timeout": config.get("DB_POOL_TIMEOUT", 30),
            "pool_recycle": config.get("DB_POOL_RECYCLE", -1),
            "pool_size": config.get("DB_POOL_SIZE", 5),
            "max_overflow": config.get("DB_MAX_OVERFLOW", 10),
            "pool_pre_ping": config.get("DB_POOL_PRE_PING", False),
        }
        super().__init__(declarative_base=Base, engine_options=engine_options)

    def setup(self):
        super().setup()
        Pin.override(self.engine, service="users-service")

    def get_dependency(self, worker_ctx):
        db = super().get_dependency(worker_ctx)
        return StorageWrapper(db, self.collections)

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Table, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType, PasswordType


Base = declarative_base()

"""SQLAlchemy Mixins"""


class IDMixin:
    id = Column(Integer, primary_key=True, nullable=False)


class CreatedTimestampMixin:
    created_datetime_utc = Column(
        DateTime, nullable=False, server_default=text("(now() at time zone 'utc')")
    )


class DeletedTimestampMixin:
    deleted_datetime_utc = Column(DateTime, nullable=True)


"""SQLAlchemy Models"""


class User(IDMixin, CreatedTimestampMixin, DeletedTimestampMixin, Base):
    __tablename__ = "users"

    email = Column(EmailType, nullable=False, index=True, unique=True)

    display_name = Column(Text, nullable=False)

    password = Column(PasswordType(schemes=["pbkdf2_sha512"]), nullable=False)

    verified = Column(Boolean, default=False, server_default="f")


class UserToken(IDMixin, CreatedTimestampMixin, Base):
    __tablename__ = "user_tokens"

    token = Column(PasswordType(schemes=["pbkdf2_sha512"]), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", primaryjoin=user_id == User.id)


class Project(IDMixin, CreatedTimestampMixin, DeletedTimestampMixin, Base):
    __tablename__ = "projects"

    name = Column(Text, nullable=False)


user_project_table = Table(
    "users_projects",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("project_id", Integer, ForeignKey("projects.id")),
)

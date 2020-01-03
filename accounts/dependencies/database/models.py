from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
    UniqueConstraint,
    text,
)
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

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", primaryjoin=user_id == User.id)


class Project(IDMixin, CreatedTimestampMixin, DeletedTimestampMixin, Base):
    __tablename__ = "projects"

    name = Column(Text, nullable=False)


class UserProject(IDMixin, CreatedTimestampMixin, Base):
    __tablename__ = "users_projects"

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="user_projects_unique_ids"),
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", primaryjoin=user_id == User.id)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    project = relationship("Project", primaryjoin=project_id == Project.id)

    verified = Column("verified", Boolean, server_default="f")

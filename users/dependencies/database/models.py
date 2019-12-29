from sqlalchemy import Column, DateTime, Integer, Text, text, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import EmailType, PasswordType


Base = declarative_base()

"""SQLAlchemy Mixins"""


class IDMixin:
    id = Column(Integer, primary_key=True, nullable=False)


class TimestampMixin:
    created_datetime_utc = Column(
        DateTime, nullable=False, server_default=text("(now() at time zone 'utc')")
    )
    deleted_datetime_utc = Column(DateTime, nullable=True)


"""SQLAlchemy Models"""


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email = Column(EmailType, nullable=False, index=True, unique=True)

    display_name = Column(Text, nullable=False)

    password = Column(PasswordType(schemes=["pbkdf2_sha512"]), nullable=False)


class Organization(IDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name = Column(Text, nullable=False)


user_organization_table = Table(
    "users_organizations",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("organization_id", Integer, ForeignKey("organizations.id")),
)

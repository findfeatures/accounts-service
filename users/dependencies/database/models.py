from sqlalchemy import Column, DateTime, Integer, Text, text
from sqlalchemy.ext.declarative import declarative_base
# install sqlalchemy_utils
from sqlalchemy_utils import EmailType, PasswordType


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)

    created_datetime_utc = Column(
        DateTime, nullable=False, server_default=text("(now() at time zone 'utc')")
    )
    deleted_datetime_utc = Column(DateTime, nullable=True)

    email = Column(EmailType, nullable=False, index=True, unique=True)

    display_name = Column(Text, nullable=False)

    password = Column(PasswordType(schemes=["pbkdf2_sha512"]), nullable=False)

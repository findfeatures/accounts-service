import datetime

import pytest
from nameko.testing.services import dummy, entrypoint_hook
from accounts.dependencies.database.models import User, UserToken
from accounts.dependencies.database.provider import Storage
from accounts.exceptions.user_tokens import InvalidToken


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def create(self, *args, **kwargs):
            return self.storage.user_tokens.create(*args, **kwargs)

        @dummy
        def verify_token(self, *args, **kwargs):
            return self.storage.user_tokens.verify_token(*args, **kwargs)

    container = container_factory(Service)
    container.start()

    return container


def test_create_user_token(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    token = "im a token"

    with entrypoint_hook(service_container, "create") as create:
        create(user.id, token)

    assert db.session.query(UserToken).count() == 1

    db.session.query(UserToken).filter_by(user_id=user.id).one()


def test_verify_token_true(db, service_container):
    token = "im a token"

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )

    user_token = UserToken(user=user, token=token)

    db.session.add(user)
    db.session.add(user_token)
    db.session.commit()

    with entrypoint_hook(service_container, "verify_token") as verify_token:
        verify_token(user.id, token)


def test_verify_token_false(db, service_container):
    token = "im a token"

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )

    user_token = UserToken(user=user, token=token)

    db.session.add(user)
    db.session.add(user_token)
    db.session.commit()

    with entrypoint_hook(service_container, "verify_token") as verify_token:
        with pytest.raises(InvalidToken):
            verify_token(user.id, "random_token")


def test_verify_token_no_token(db, service_container):

    with entrypoint_hook(service_container, "verify_token") as verify_token:
        with pytest.raises(InvalidToken):
            verify_token(123, "random_token")


def test_verify_token_multiple_tokens(db, service_container):
    token = "im a token"

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )

    user_token_1 = UserToken(
        user=user,
        token=token,
        created_datetime_utc=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )

    user_token_2 = UserToken(
        user=user, token=token + "123", created_datetime_utc=datetime.datetime.utcnow()
    )

    db.session.add(user)
    db.session.add(user_token_1)
    db.session.add(user_token_2)

    db.session.commit()

    with entrypoint_hook(service_container, "verify_token") as verify_token:
        verify_token(user.id, token + "123")

import pytest
from mock import ANY
from nameko.testing.services import dummy, entrypoint_hook

from users.dependencies.database.models import UserToken, User
from users.dependencies.database.provider import Storage


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "users"

        storage = Storage()

        @dummy
        def create(self, *args, **data):
            return self.storage.user_tokens.create(*args, **data)

    container = container_factory(Service)
    container.start()

    return container


def test_create_user_token(db, service_container):
    user = User(
        email="TEST@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    token = "im a token"

    with entrypoint_hook(service_container, "create") as create:
        create(user.id, token)

    assert db.session.query(UserToken).count() == 1

    db.session.query(UserToken).filter_by(user_id=user.id).one()


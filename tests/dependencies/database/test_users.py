import datetime

import pytest
from nameko.testing.services import dummy, entrypoint_hook
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from users.dependencies.database.models import User
from users.dependencies.database.provider import Storage


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "users"

        storage = Storage()

        @dummy
        def get(self, *args, **data):
            return self.storage.users.get(*args, **data)

        @dummy
        def get_from_email(self, *args, **data):
            return self.storage.users.get_from_email(*args, **data)

        @dummy
        def create(self, *args, **data):
            return self.storage.users.create(*args, **data)

        @dummy
        def delete(self, *args, **data):
            return self.storage.users.delete(*args, **data)

        @dummy
        def is_correct_password(self, *args, **data):
            return self.storage.users.is_correct_password(*args, **data)

    container = container_factory(Service)
    container.start()

    return container


def test_get_user_successful(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "get") as get:
        user_details = get(user.id)

    assert user_details == {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "created_datetime_utc": user.created_datetime_utc,
        "deleted_datetime_utc": user.deleted_datetime_utc,  # None,
    }


def test_get_user_unsuccessful(db, service_container):
    with entrypoint_hook(service_container, "get") as get:
        with pytest.raises(orm_exc.NoResultFound):
            get(1)


def test_get_user_from_email_successful(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "get_from_email") as get_from_email:
        user_details = get_from_email(user.email)

    assert user_details == {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "created_datetime_utc": user.created_datetime_utc,
        "deleted_datetime_utc": user.deleted_datetime_utc,  # None,
    }


def test_get_user_from_email_unsuccessful(db, service_container):
    with entrypoint_hook(service_container, "get_from_email") as get_from_email:
        with pytest.raises(orm_exc.NoResultFound):
            get_from_email("test@google.com")


def test_create_user_successful(db, service_container):

    email = "TEST@google.com"
    password = "password"
    display_name = "Test Account"

    with entrypoint_hook(service_container, "create") as create:
        user_id = create(email, password, display_name)

    assert db.session.query(User).count() == 1

    user = db.session.query(User).get(user_id)

    assert user.display_name == display_name
    assert user.email == email.lower()  # should be lower cased in the db
    assert user.password == password
    assert user.deleted_datetime_utc is None


def test_create_user_unsuccessful(db, service_container):

    email = "test@google.com"
    password = "password"
    display_name = "Test Account"

    db.session.add(User(email=email, password=password, display_name=display_name))
    db.session.commit()

    with entrypoint_hook(service_container, "create") as create:
        with pytest.raises(exc.IntegrityError):
            create(email, password, display_name)


def test_delete_user_successful(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "delete") as delete:
        delete(user.id)

    db.session.commit()  # not sure why this is needed but it seems to fix the test?
    # its definitely commit in production but weird its not here.

    assert db.session.query(User).count() == 1

    deleted_user = db.session.query(User).filter_by(id=user.id).one()

    assert deleted_user.deleted_datetime_utc is not None


def test_is_correct_password_true(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(
        service_container, "is_correct_password"
    ) as is_correct_password:
        result = is_correct_password(user.email, "password")

        assert result is True


def test_is_correct_password_false(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(
        service_container, "is_correct_password"
    ) as is_correct_password:
        result = is_correct_password(user.email, "not_the_password")

        assert result is False


def test_is_correct_password_false_with_missing_user(db, service_container):

    with entrypoint_hook(
        service_container, "is_correct_password"
    ) as is_correct_password:
        result = is_correct_password("test@google.com", "password")

        assert result is False


def test_is_correct_password_false_with_deleted_user(db, service_container):
    user = User(
        email="test@google.com",
        password="password",
        display_name="Test Account",
        deleted_datetime_utc=datetime.datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(
        service_container, "is_correct_password"
    ) as is_correct_password:
        result = is_correct_password("test@google.com", "password")

        assert result is False

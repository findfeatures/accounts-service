import datetime

import pytest
from nameko.testing.services import dummy, entrypoint_hook
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from accounts.dependencies.database.models import User
from accounts.dependencies.database.provider import Storage


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def get(self, *args, **kwargs):
            return self.storage.users.get(*args, **kwargs)

        @dummy
        def get_from_email(self, *args, **kwargs):
            return self.storage.users.get_from_email(*args, **kwargs)

        @dummy
        def create(self, *args, **kwargs):
            return self.storage.users.create(*args, **kwargs)

        @dummy
        def delete(self, *args, **kwargs):
            return self.storage.users.delete(*args, **kwargs)

        @dummy
        def is_correct_password(self, *args, **kwargs):
            return self.storage.users.is_correct_password(*args, **kwargs)

        @dummy
        def update_verified(self, *args, **kwargs):
            return self.storage.users.update_verified(*args, **kwargs)

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
        "verified": False,
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
        "verified": False,
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
        email="test@google.com",
        password="password",
        display_name="Test Account",
        verified=True,
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
        email="test@google.com",
        password="password",
        display_name="Test Account",
        verified=True,
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


def test_update_verified_true(db, service_container):
    user = User(
        email="test@google.com",
        password="password",
        display_name="Test Account",
        deleted_datetime_utc=datetime.datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()

    assert user.verified is False

    with entrypoint_hook(service_container, "update_verified") as update_verified:
        update_verified(user.id, True)
    db.session.commit()

    user_from_db = db.session.query(User).get(user.id)

    assert user_from_db.verified is True


def test_update_verified_user_doesnt_exist(db, service_container):

    with entrypoint_hook(service_container, "update_verified") as update_verified:
        with pytest.raises(orm_exc.NoResultFound):
            update_verified(3, True)

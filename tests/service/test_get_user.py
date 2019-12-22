import datetime

import pytest
from mock import call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy.orm import exc as orm_exc
from users.service import UsersService


def test_get_successful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    email = "test@google.com"
    created_datetime_utc = datetime.datetime.utcnow()
    deleted_datetime_utc = None

    storage.users.get.return_value = {
        "id": user_id,
        "email": email,
        "created_datetime_utc": created_datetime_utc,
        "deleted_datetime_utc": deleted_datetime_utc,
    }

    with entrypoint_hook(container, "get_user") as get_user:
        result = get_user(user_id=user_id)

        assert storage.users.get.call_args == call(123)

        assert result == {
            "id": user_id,
            "email": email,
            "created_datetime_utc": created_datetime_utc.isoformat(),
            "deleted_datetime_utc": None,
        }


def test_get_successful_with_deleted_datetime(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    email = "test@google.com"
    created_datetime_utc = datetime.datetime.utcnow()
    deleted_datetime_utc = datetime.datetime.utcnow()

    storage.users.get.return_value = {
        "id": user_id,
        "email": email,
        "created_datetime_utc": created_datetime_utc,
        "deleted_datetime_utc": deleted_datetime_utc,
    }

    with entrypoint_hook(container, "get_user") as get_user:
        result = get_user(user_id=user_id)

        assert storage.users.get.call_args == call(123)

        assert result == {
            "id": user_id,
            "email": email,
            "created_datetime_utc": created_datetime_utc.isoformat(),
            "deleted_datetime_utc": deleted_datetime_utc.isoformat(),
        }


def test_get_unsuccessful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.get.side_effect = orm_exc.NoResultFound()

    with entrypoint_hook(container, "get_user") as get_user:
        with pytest.raises(ValueError):
            get_user(user_id=123)

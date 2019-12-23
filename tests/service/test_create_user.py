import pytest
from mock import call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy import exc
from users.service import UsersService
from users.exceptions import UserAlreadyExists

def test_create_user_successful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.create.return_value = 1

    payload = {
        "email": "test@email.com",
        "password": "password",
        "display_name": "Test Account",
    }
    with entrypoint_hook(container, "create_user") as create_user:
        result = create_user(user_details=payload)

        # can't really check the
        assert result == 1

        assert storage.users.create.call_args == call(
            payload["email"], payload["password"], payload["display_name"]
        )


def test_create_user_unsuccessful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.create.side_effect = exc.IntegrityError(
        statement="", params="", orig=""
    )

    payload = {
        "email": "test@email.com",
        "password": "password",
        "display_name": "Test Account",
    }
    with entrypoint_hook(container, "create_user") as create_user:

        with pytest.raises(UserAlreadyExists):
            create_user(user_details=payload)

        assert storage.users.create.call_args == call(
            payload["email"], payload["password"], payload["display_name"]
        )

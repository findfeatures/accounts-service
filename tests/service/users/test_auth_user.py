import pytest
from mock import ANY, call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from users.exceptions.users import UserNotAuthorised, UserNotVerified
from users.service import UsersService


def test_auth_successful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    email = "test@google.com"
    password = "password"

    storage.users.is_correct_password.return_value = True
    storage.users.get_from_email.return_value = {"id": user_id, "email": email, "verified": True}

    with entrypoint_hook(container, "auth_user") as auth_user:
        result = auth_user(email=email, password=password)

        assert result == {"JWT": ANY}

        assert storage.users.is_correct_password.call_args == call(email, password)

        assert storage.users.get_from_email.call_args == call(email)


def test_auth_unsuccessful(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.is_correct_password.return_value = False

    email = "test@google.com"
    password = "password"

    with entrypoint_hook(container, "auth_user") as auth_user:
        with pytest.raises(UserNotAuthorised):
            auth_user(email=email, password=password)

        assert storage.users.is_correct_password.call_args == call(email, password)
        assert storage.users.get_from_email.called is False


def test_auth_successful_but_not_verified(config, runner_factory):
    runner = runner_factory(UsersService)
    container = get_container(runner, UsersService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    email = "test@google.com"
    password = "password"

    storage.users.is_correct_password.return_value = True
    storage.users.get_from_email.return_value = {"id": user_id, "email": email,
                                                 "verified": False}

    with entrypoint_hook(container, "auth_user") as auth_user:
        with pytest.raises(UserNotVerified):
            auth_user(email=email, password=password)

        assert storage.users.is_correct_password.call_args == call(email, password)

        assert storage.users.get_from_email.call_args == call(email)

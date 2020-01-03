import pytest
from accounts.exceptions.users import UserAlreadyExists
from accounts.service import AccountsService
from mock import call, patch
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy import exc


def test_create_user_successful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage, send_grid = replace_dependencies(container, "storage", "send_grid")
    runner.start()

    storage.users.create.return_value = 1
    storage.user_tokens.create.return_value = "randomtoken"

    payload = {
        "email": "test@email.com",
        "password": "password",
        "display_name": "Test Account",
    }
    with entrypoint_hook(container, "create_user") as create_user:
        with patch("accounts.service.users.generate_token", return_value="token"):

            result = create_user(user_details=payload)

        assert result == 1

        assert storage.users.create.call_args == call(
            payload["email"], payload["password"], payload["display_name"]
        )

        assert send_grid.send_signup_verification.call_args == call(
            payload["email"], "token"
        )


def test_create_user_unsuccessful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
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

import pytest
from mock import call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy.orm import exc as orm_exc
from accounts.exceptions.user_tokens import InvalidToken
from accounts.exceptions.users import UserNotAuthorised
from accounts.service import AccountsService


def test_verify_user_verified(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    token = "token"
    email = "test@google.com"

    storage.users.get_from_email.return_value = {"id": user_id, "email": email}
    storage.user_tokens.verify_token.return_value = None
    storage.users.update_verified.return_value = None

    with entrypoint_hook(container, "verify_user") as verify_user:
        verify_user(email=email, token=token)

        assert storage.users.get_from_email.call_args == call(email)
        assert storage.user_tokens.verify_token.call_args == call(user_id, token)
        assert storage.users.update_verified.call_args == call(user_id, True)


def test_verify_user_missing_user(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    token = "token"
    email = "test@google.com"

    storage.users.get_from_email.side_effect = orm_exc.NoResultFound()

    with entrypoint_hook(container, "verify_user") as verify_user:
        with pytest.raises(UserNotAuthorised):
            verify_user(email=email, token=token)

        assert storage.users.get_from_email.call_args == call(email)


def test_verify_user_invalid_token(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    token = "token"
    email = "test@google.com"

    storage.users.get_from_email.return_value = {"id": user_id, "email": email}
    storage.user_tokens.verify_token.side_effect = InvalidToken()

    with entrypoint_hook(container, "verify_user") as verify_user:
        with pytest.raises(UserNotAuthorised):
            verify_user(email=email, token=token)

        assert storage.users.get_from_email.call_args == call(email)

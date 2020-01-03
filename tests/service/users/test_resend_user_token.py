import datetime

import pytest
from accounts.exceptions.users import UserNotAuthorised
from accounts.service import AccountsService
from mock import ANY, call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy.orm import exc as orm_exc


def test_resend_user_token(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage, sendgrid = replace_dependencies(container, "storage", "sendgrid")
    runner.start()

    email = "test@google.com"
    password = "password"
    user_id = 1

    storage.users.is_correct_password.return_value = True

    storage.users.get_from_email.return_value = {
        "id": user_id,
        "email": email,
        "verified": False,
    }

    storage.user_tokens.create.return_value = None

    sendgrid.send_signup_verification.return_value = None

    with entrypoint_hook(container, "resend_user_token") as resend_user_token:
        result = resend_user_token(email, password)

        assert storage.users.is_correct_password.call_args == call(email, password)

        assert storage.users.get_from_email.call_args == call(email)

        assert storage.user_tokens.create.call_args == call(user_id, ANY)

        assert sendgrid.send_signup_verification.call_args == call(email, ANY)

        assert result is None


def test_resend_user_token_invalid_password(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage, sendgrid = replace_dependencies(container, "storage", "sendgrid")
    runner.start()

    email = "test@google.com"
    password = "password"

    storage.users.is_correct_password.return_value = False

    with entrypoint_hook(container, "resend_user_token") as resend_user_token:

        with pytest.raises(UserNotAuthorised):
            resend_user_token(email, password)

        assert storage.users.is_correct_password.call_args == call(email, password)


def test_resend_user_token_already_verified(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage, sendgrid = replace_dependencies(container, "storage", "sendgrid")
    runner.start()

    email = "test@google.com"
    password = "password"
    user_id = 1

    storage.users.is_correct_password.return_value = True

    storage.users.get_from_email.return_value = {
        "id": user_id,
        "email": email,
        "verified": True,
    }

    with entrypoint_hook(container, "resend_user_token") as resend_user_token:
        with pytest.raises(UserNotAuthorised):
            resend_user_token(email, password)

        assert storage.users.is_correct_password.call_args == call(email, password)

        assert storage.users.get_from_email.call_args == call(email)

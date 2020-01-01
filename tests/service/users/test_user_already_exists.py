from accounts.service import AccountsService
from mock import call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy.orm import exc as orm_exc


def test_user_already_exists_true(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123
    email = "test@google.com"

    storage.users.get_from_email.return_value = {"id": user_id, "email": email}

    with entrypoint_hook(container, "user_already_exists") as user_already_exists:
        result = user_already_exists(email=email)

        assert result is True

        assert storage.users.get_from_email.call_args == call(email)


def test_user_already_exists_false(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    email = "test@google.com"

    storage.users.get_from_email.side_effect = orm_exc.NoResultFound()

    with entrypoint_hook(container, "user_already_exists") as user_already_exists:
        result = user_already_exists(email=email)

        assert result is False

        assert storage.users.get_from_email.call_args == call(email)

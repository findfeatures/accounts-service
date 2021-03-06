import pytest
from accounts.exceptions.users import UserDoesNotExist
from accounts.service import AccountsService
from mock import call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container
from sqlalchemy.orm import exc as orm_exc


def test_delete_user_successful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.delete.return_value = None

    user_id = 1

    with entrypoint_hook(container, "delete_user") as delete_user:
        result = delete_user(user_id=user_id)

        assert result is None

        assert storage.users.delete.call_args == call(user_id)


def test_delete_user_unsuccessful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    storage.users.delete.side_effect = orm_exc.NoResultFound()

    user_id = 100

    with entrypoint_hook(container, "delete_user") as delete_user:
        with pytest.raises(UserDoesNotExist):
            delete_user(user_id=user_id)

        assert storage.users.delete.call_args == call(user_id)

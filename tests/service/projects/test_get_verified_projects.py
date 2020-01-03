import datetime

from accounts.service import AccountsService
from mock import ANY, call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container


def test_get_verified_projects(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123

    created = datetime.datetime.utcnow()

    storage.projects.get_all_verified.return_value = [
        {
            "id": 1,
            "name": "test",
            "created_datetime_utc": created,
            "deleted_datetime_utc": None,
        },
        {
            "id": 2,
            "name": "another test",
            "created_datetime_utc": created,
            "deleted_datetime_utc": None,
        },
    ]

    with entrypoint_hook(container, "get_verified_projects") as get_verified_projects:
        result = get_verified_projects(user_id)

        assert storage.projects.get_all_verified.call_args == call(user_id)

        assert result == [
            {"id": 1, "name": "test", "created_datetime_utc": created.isoformat()},
            {
                "id": 2,
                "name": "another test",
                "created_datetime_utc": created.isoformat(),
            },
        ]


def test_get_verified_projects_none(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    storage = replace_dependencies(container, "storage")
    runner.start()

    user_id = 123

    storage.projects.get_all_verified.return_value = []

    with entrypoint_hook(container, "get_verified_projects") as get_verified_projects:
        result = get_verified_projects(user_id)

        assert storage.projects.get_all_verified.call_args == call(user_id)

        assert result == []

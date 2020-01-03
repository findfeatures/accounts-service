import datetime

import pytest
from accounts.dependencies.database.models import Project, User, UserProject
from accounts.dependencies.database.provider import Storage
from nameko.testing.services import dummy, entrypoint_hook
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def get_all_verified(self, *args, **kwargs):
            return self.storage.projects.get_all_verified(*args, **kwargs)

    container = container_factory(Service)
    container.start()

    return container


def test_get_all_verified_none(db, service_container):
    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "get_all_verified") as get_all_verified:
        projects = get_all_verified(user.id)

    assert projects == []


def test_get_all_verified(db, service_container):

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    project_one = Project(
        name="Project One", created_datetime_utc=datetime.datetime.utcnow()
    )
    project_two = Project(
        name="Project Two",
        created_datetime_utc=datetime.datetime.utcnow() + datetime.timedelta(days=1),
    )
    project_three = Project(
        name="Project Three",
        created_datetime_utc=datetime.datetime.utcnow() + datetime.timedelta(days=2),
    )

    user_project_1 = UserProject(user=user, project=project_one, verified=True)
    user_project_2 = UserProject(user=user, project=project_two, verified=False)
    user_project_3 = UserProject(user=user, project=project_three, verified=True)

    db.session.add_all(
        [
            user,
            project_one,
            project_two,
            project_three,
            user_project_1,
            user_project_2,
            user_project_3,
        ]
    )
    db.session.commit()

    with entrypoint_hook(service_container, "get_all_verified") as get_all_verified:
        projects = get_all_verified(user.id)

    assert projects == [
        {
            "id": project_one.id,
            "name": project_one.name,
            "created_datetime_utc": project_one.created_datetime_utc,
            "deleted_datetime_utc": None,
        },
        {
            "id": project_three.id,
            "name": project_three.name,
            "created_datetime_utc": project_three.created_datetime_utc,
            "deleted_datetime_utc": None,
        },
    ]

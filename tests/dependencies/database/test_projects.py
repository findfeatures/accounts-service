import datetime

import mock
import pytest
from accounts.dependencies.database.models import (
    Project,
    StripeSessionCompleted,
    StripeSessionCompletedStatusEnum,
    User,
    UserProject,
)
from accounts.dependencies.database.provider import Storage
from mock import call
from nameko.testing.services import dummy, entrypoint_hook


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def get_total_projects(self, *args, **kwargs):
            return self.storage.projects.get_total_projects(*args, **kwargs)

        @dummy
        def get_all_verified(self, *args, **kwargs):
            return self.storage.projects.get_all_verified(*args, **kwargs)

    container = container_factory(Service)
    container.start()

    return container


def test_get_total_projects_none(db, service_container):

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "get_total_projects") as get_total_projects:
        with mock.patch(
            "accounts.dependencies.database.collections.projects.Projects.get_all_verified",
            return_value=[],
        ) as get_all_verified:
            total_projects = get_total_projects(user.id)

        assert get_all_verified.call_args == call(user.id)

    assert total_projects == 0


def test_get_total_projects(db, service_container):

    user = User(
        email="test@google.com", password="password", display_name="Test Account"
    )
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(service_container, "get_total_projects") as get_total_projects:
        with mock.patch(
            "accounts.dependencies.database.collections.projects.Projects.get_all_verified",
            return_value=[{}, {}],
        ) as get_all_verified:
            total_projects = get_total_projects(user.id)

        assert get_all_verified.call_args == call(user.id)

    assert total_projects == 2


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
        name="Project One",
        created_datetime_utc=datetime.datetime.utcnow(),
        checkout_session_id="1",
    )
    project_two = Project(
        name="Project Two",
        created_datetime_utc=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        checkout_session_id="2",
    )
    project_three = Project(
        name="Project Three",
        created_datetime_utc=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        checkout_session_id="3",
    )
    project_four = Project(
        name="Project Four",
        created_datetime_utc=datetime.datetime.utcnow() + datetime.timedelta(days=2),
        checkout_session_id="4",
    )

    """
    event_id = Column(Text, index=True, nullable=False)
    session_id = Column(Text, index=True, nullable=False)
    status = Column(Enum(StripeSessionCompletedStatusEnum), nullable=False)
    event_data = Column(JSON, nullable=False)
    """
    stripe_session_completed_1 = StripeSessionCompleted(
        event_id=1,
        session_id="1",
        status=StripeSessionCompletedStatusEnum.finished,
        event_data={},
    )
    stripe_session_completed_3 = StripeSessionCompleted(
        event_id=3,
        session_id="3",
        status=StripeSessionCompletedStatusEnum.finished,
        event_data={},
    )
    stripe_session_completed_4 = StripeSessionCompleted(
        event_id=4,
        session_id="4",
        status=StripeSessionCompletedStatusEnum.processing,
        event_data={},
    )

    user_project_1 = UserProject(user=user, project=project_one, verified=True)
    user_project_2 = UserProject(user=user, project=project_two, verified=False)
    user_project_3 = UserProject(user=user, project=project_three, verified=True)
    user_project_4 = UserProject(user=user, project=project_four, verified=True)

    db.session.add_all(
        [
            user,
            project_one,
            project_two,
            project_three,
            user_project_1,
            user_project_2,
            user_project_3,
            stripe_session_completed_1,
            stripe_session_completed_3,
            stripe_session_completed_4,
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
            "checkout_session_id": "1",
        },
        {
            "id": project_three.id,
            "name": project_three.name,
            "created_datetime_utc": project_three.created_datetime_utc,
            "deleted_datetime_utc": None,
            "checkout_session_id": "3",
        },
    ]

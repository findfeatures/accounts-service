import pytest
from accounts.dependencies.database.models import User, UserNotification
from accounts.dependencies.database.provider import Storage
from nameko.testing.services import dummy, entrypoint_hook


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def create_notification(self, *args, **kwargs):
            return self.storage.user_notifications.create_notification(*args, **kwargs)

    container = container_factory(Service)
    container.start()

    return container


def test_create_audit_log(db, service_container):
    user = User(email="test", display_name="test", password="test")
    db.session.add(user)
    db.session.commit()

    with entrypoint_hook(
        service_container, "create_notification"
    ) as create_notification:
        create_notification(user.id, "TEST", {"data": "test"})

    db.session.commit()

    notification_result = (
        db.session.query(UserNotification).filter_by(user_id=user.id).all()
    )

    assert len(notification_result) == 1

    assert notification_result[0].notification_type == "TEST"
    assert notification_result[0].meta_data == {"data": "test"}

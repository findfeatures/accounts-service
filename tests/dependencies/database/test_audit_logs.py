import datetime

import mock
import pytest
from accounts.dependencies.database.models import Project, AuditLog
from accounts.dependencies.database.provider import Storage
from nameko.testing.services import dummy, entrypoint_hook


@pytest.fixture
def service_container(db, container_factory):
    class Service:
        name = "accounts"

        storage = Storage()

        @dummy
        def create_log(self, *args, **kwargs):
            return self.storage.audit_logs.create_log(*args, **kwargs)

    container = container_factory(Service)
    container.start()

    return container


def test_create_audit_log(db, service_container):
    project = Project(name="test")
    db.session.add(project)
    db.session.commit()

    with entrypoint_hook(service_container, "create_log") as create_log:
        create_log(project.id, "TEST", {"data": "test"})

    db.session.commit()

    audit_log_result = db.session.query(AuditLog).filter_by(project_id=project.id).all()

    assert len(audit_log_result) == 1

    assert audit_log_result[0].log_type == "TEST"
    assert audit_log_result[0].meta_data == {"data": "test"}

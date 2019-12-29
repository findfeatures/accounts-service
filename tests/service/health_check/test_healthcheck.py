from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies
from users.dependencies.database.provider import Storage, StorageWrapper
from users.service import UsersService


def test_healthcheck(config, db, web_session):
    container = ServiceContainer(UsersService)
    replace_dependencies(container, storage=StorageWrapper(db, Storage.collections))
    container.start()

    response = web_session.get("/health-check")
    assert response.status_code == 200

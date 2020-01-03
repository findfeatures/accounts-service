import pytest
from accounts.dependencies.redis.provider import Redis
from mock import Mock


@pytest.fixture
def redis_dependency(config):
    dependency = Redis()
    dependency.container = Mock()

    return dependency


# todo: add some more unit tests here for the dependency. Can checkout out the stripe
# unit tests in the accounts service


def test_redis_stop(redis_dependency):
    redis_dependency.setup()
    redis_dependency.start()
    redis_dependency.stop()

    assert redis_dependency.client is None


def test_redis_kill(redis_dependency):
    redis_dependency.setup()
    redis_dependency.start()
    redis_dependency.kill()

    assert redis_dependency.client is None


def test_redis_get_dependency(redis_dependency):
    redis_dependency.setup()
    redis_dependency.start()
    client = redis_dependency.get_dependency(Mock())

    assert client is not None

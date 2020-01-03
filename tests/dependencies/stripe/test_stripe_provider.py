import pytest
from accounts.dependencies.stripe.provider import Stripe
from mock import Mock, call, patch


@pytest.fixture
def stripe_dependency(config):
    dependency = Stripe()
    dependency.container = Mock()

    return dependency


def test_stripe_setup(stripe_dependency):
    stripe_dependency.setup()

    assert stripe_dependency.api_key == "sk_test_bfLXLv5bBvHa3fJALYMPXh4M00YfZEL2Cz"


def test_stripe_start(stripe_dependency, mock_stripe):
    stripe_dependency.setup()
    stripe_dependency.start()

    assert stripe_dependency.client == mock_stripe
    assert (
        stripe_dependency.client.api_key == "sk_test_bfLXLv5bBvHa3fJALYMPXh4M00YfZEL2Cz"
    )


def test_stripe_stop(stripe_dependency):
    stripe_dependency.setup()
    stripe_dependency.start()
    stripe_dependency.stop()

    assert stripe_dependency.client is None


def test_stripe_kill(stripe_dependency):
    stripe_dependency.setup()
    stripe_dependency.start()
    stripe_dependency.kill()

    assert stripe_dependency.client is None


def test_stripe_get_dependency(stripe_dependency, mock_stripe):
    stripe_dependency.setup()
    stripe_dependency.start()
    client = stripe_dependency.get_dependency(Mock())

    assert client == mock_stripe

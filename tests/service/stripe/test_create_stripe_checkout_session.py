import pytest
import stripe as stripe_payment
from accounts.exceptions.stripe import UnableToCreateCheckoutSession
from accounts.service import AccountsService
from mock import Mock, call
from nameko.testing.services import entrypoint_hook, replace_dependencies
from nameko.testing.utils import get_container


def test_create_stripe_checkout_session_successful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    stripe = replace_dependencies(container, "stripe")
    runner.start()

    user_id = 123
    email = "test@google.com"
    plan = "plan1"
    success_url = "http://success.com"
    cancel_url = "http://cancel.com"

    stripe.checkout.Session.create.return_value = Mock(id="session_id")

    with entrypoint_hook(
        container, "create_stripe_checkout_session"
    ) as create_stripe_checkout_session:
        result = create_stripe_checkout_session(
            {
                "user_id": user_id,
                "email": email,
                "plan": plan,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
        )

        assert result == "session_id"

        assert stripe.checkout.Session.create.call_args == call(
            customer_email=email,
            payment_method_types=["card"],
            subscription_data={"items": [{"plan": plan}]},
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )


def test_create_stripe_checkout_session_unsuccessful(config, runner_factory):
    runner = runner_factory(AccountsService)
    container = get_container(runner, AccountsService)
    stripe = replace_dependencies(container, "stripe")
    runner.start()

    user_id = 123
    email = "test@google.com"
    plan = "plan1"
    success_url = "http://success.com"
    cancel_url = "http://cancel.com"

    stripe.checkout.Session.create.side_effect = stripe_payment.error.StripeError()

    with entrypoint_hook(
        container, "create_stripe_checkout_session"
    ) as create_stripe_checkout_session:
        with pytest.raises(UnableToCreateCheckoutSession):
            create_stripe_checkout_session(
                {
                    "user_id": user_id,
                    "email": email,
                    "plan": plan,
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                }
            )

import logging

import stripe as stripe_payments
from accounts import schemas, utils
from accounts.service.base import ServiceMixin
from nameko import config
from nameko.rpc import rpc


logger = logging.getLogger(__name__)

# todo: maybe move this into a dependency instead!
stripe_payments.api_key = config.get("STRIPE_PAYMENT_API_KEY")


class StripeServiceMixin(ServiceMixin):
    @rpc(expected_exceptions=())
    @utils.log_entrypoint
    def create_stripe_checkout_session(self, checkout_details):
        checkout_details = schemas.CreateStripeCheckoutSessionRequest().load(
            checkout_details
        )

        # todo: error handling!
        session = stripe_payments.checkout.Session.create(
            customer_email=checkout_details["email"],
            payment_method_types=["card"],
            subscription_data={"items": [{"plan": checkout_details["plan"]}]},
            success_url=checkout_details["success_url"]
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=checkout_details["cancel_url"],
        )

        return session.id

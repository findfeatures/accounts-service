import logging

import stripe
from accounts import schemas, utils
from accounts.exceptions.stripe import UnableToCreateCheckoutSession
from accounts.service.base import ServiceMixin
from nameko.rpc import rpc


logger = logging.getLogger(__name__)


class StripeServiceMixin(ServiceMixin):
    @rpc(expected_exceptions=(UnableToCreateCheckoutSession,))
    @utils.log_entrypoint
    def create_stripe_checkout_session(self, checkout_details):
        checkout_details = schemas.CreateStripeCheckoutSessionRequest().load(
            checkout_details
        )

        try:
            session = self.stripe.checkout.Session.create(
                customer_email=checkout_details["email"],
                payment_method_types=["card"],
                subscription_data={"items": [{"plan": checkout_details["plan"]}]},
                success_url=checkout_details["success_url"]
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=checkout_details["cancel_url"],
            )
        except stripe.error.StripeError as e:
            logger.error(e)
            raise UnableToCreateCheckoutSession(
                "Failed to create a new checkout session for user"
            )

        return session.id

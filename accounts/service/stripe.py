import logging
import time

import stripe
from accounts import schemas, utils
from accounts.dependencies.database.models import StripeSessionCompletedStatusEnum
from accounts.dependencies.redis.provider import NonBlockingLock
from accounts.entrypoints import stripe as nameko_stripe
from accounts.exceptions.projects import CheckoutSessionAlreadyExists
from accounts.exceptions.stripe import UnableToCreateCheckoutSession
from accounts.service.base import ServiceMixin
from nameko.rpc import rpc
from sqlalchemy.orm import exc as orm_exc


logger = logging.getLogger(__name__)


class StripeServiceMixin(ServiceMixin):
    @nameko_stripe.consume(
        {
            "type": "checkout.session.completed",
            "created": {
                # Check for events created in the last 6 number of hours.
                "gte": int(time.time() - 6 * 60 * 60)
            },
            "limit": 100,
        },
        polling_period=5,
    )
    def stripe_process_checkout_completed(self, event):
        event_id = event["id"]
        session_id = event["data"]["object"]["id"]

        # time to live in milliseconds (30 seconds)
        lock = NonBlockingLock(
            self.redis,
            f"stripe-process-checkout-lock:{event_id}",
            ttl=30 * 1000,
            lock_id=event_id,
        )

        with lock:
            try:
                db_event = self.storage.stripe_sessions_completed.get_event(event_id)

                if db_event["status"] == StripeSessionCompletedStatusEnum.finished:
                    logger.info(
                        f"skipping checkout.session.completed"
                        f" with id {event_id} as already finished processing"
                    )
                    return
            except orm_exc.NoResultFound:
                logger.info(
                    f"processing checkout.session.completed"
                    f" id {event_id} for the first time"
                )

                self.storage.stripe_sessions_completed.create(
                    event_id, session_id, event
                )

            self.storage.stripe_sessions_completed.mark_as_finished(event_id)
            logger.info(f"finished processing event with id {event_id}")

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

            # raises CheckoutSessionAlreadyExists if project already has session id
            self.storage.projects.set_checkout_session_id(
                checkout_details["project_id"], session.id
            )

        except (stripe.error.StripeError, CheckoutSessionAlreadyExists) as e:
            logger.error(e)
            raise UnableToCreateCheckoutSession(
                "Failed to create a new checkout session for user"
            )

        return session.id

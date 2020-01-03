from accounts.dependencies.database.collections import Collection
from accounts.dependencies.database.models import (
    StripeSessionCompleted,
    StripeSessionCompletedStatusEnum,
)
from accounts.utils import sa_to_dict


class StripeSessionsCompleted(Collection):
    name = "stripe_sessions_completed"
    model = StripeSessionCompleted

    @sa_to_dict()
    def get_event(self, event_id):
        result = self.db.session.query(self.model).filter_by(event_id=event_id).one()
        return result

    def create(self, event_id, session_id, event_data):
        new_event = self.model(
            event_id=event_id,
            session_id=session_id,
            status=StripeSessionCompletedStatusEnum.processing,
            event_data=event_data,
        )
        with self.db.get_session() as session:
            session.add(new_event)

    def mark_as_finished(self, event_id):
        with self.db.get_session() as session:
            result = session.query(self.model).filter_by(event_id=event_id).one()

            result.status = StripeSessionCompletedStatusEnum.finished

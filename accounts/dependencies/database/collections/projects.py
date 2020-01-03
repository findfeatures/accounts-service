from accounts.dependencies.database.collections import Collection
from accounts.dependencies.database.models import (
    Project,
    StripeSessionCompleted,
    StripeSessionCompletedStatusEnum,
    UserProject,
)
from accounts.exceptions.projects import CheckoutSessionAlreadyExists
from accounts.utils import _sa_to_dict


class Projects(Collection):
    name = "projects"
    model = Project

    def get_total_projects(self, user_id):
        return len(self.get_all_verified(user_id))

    def get_all_verified(self, user_id):
        # filters out projects which user isn't verified for and
        # where not paid yet.
        projects_data = (
            self.db.session.query(self.model)
            .join(UserProject)
            .join(
                StripeSessionCompleted,
                StripeSessionCompleted.session_id == self.model.checkout_session_id,
                isouter=True,
            )
            .filter(
                UserProject.user_id == user_id,
                UserProject.verified.is_(True),
                StripeSessionCompleted.id.isnot(None),
                StripeSessionCompleted.status
                == StripeSessionCompletedStatusEnum.finished,
            )
            .order_by(UserProject.created_datetime_utc)
            .all()
        )
        result = []

        for project in projects_data:
            result.append(_sa_to_dict(project))

        return result

    def set_checkout_session_id(self, project_id, checkout_session_id):

        with self.db.get_session() as session:
            project = session.query(self.model).get(project_id)

            if project.checkout_session_id:
                raise CheckoutSessionAlreadyExists(
                    f"checkout_session_id is already defined for {project_id}"
                )

            project.checkout_session_id = checkout_session_id

from accounts.dependencies.database.collections import Collection
from accounts.dependencies.database.models import Project, UserProject
from accounts.utils import _sa_to_dict


class Projects(Collection):
    name = "projects"
    model = Project

    def get_all_verified(self, user_id):
        projects_data = (
            self.db.session.query(self.model)
            .join(UserProject)
            .filter(UserProject.user_id == user_id, UserProject.verified.is_(True))
            .order_by(UserProject.created_datetime_utc)
            .all()
        )
        result = []

        for project in projects_data:
            result.append(_sa_to_dict(project))

        return result

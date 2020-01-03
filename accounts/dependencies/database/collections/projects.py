from accounts.dependencies.database.collections import Collection
from accounts.dependencies.database.models import Project, UserProject


class Projects(Collection):
    name = "projects"
    model = Project

    def get_all_verified(self, user_id):
        project_data = (
            self.db.query(self.model)
            .join(UserProject)
            .filter(UserProject.user_id == user_id, UserProject.verified.is_(True))
            .all()
        )
        import pdb

        pdb.set_trace()
        pass

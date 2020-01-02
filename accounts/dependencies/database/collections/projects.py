from accounts.dependencies.database.collections import Collection
from accounts.dependencies.database.models import Project


class Projects(Collection):
    name = "projects"
    model = Project

    def create(self, name):
        new_project = self.model(name=name)

        with self.db.get_session() as session:
            session.add(new_project)

        return new_project.id

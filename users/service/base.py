from users.dependencies.database.provider import Storage


class ServiceMixin:
    name = "users"

    storage = Storage()

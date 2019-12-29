from users.dependencies.database.provider import Storage
from users.dependencies.sendgrid.provider import SendGrid


class ServiceMixin:
    name = "users"

    storage = Storage()
    sendgrid = SendGrid()

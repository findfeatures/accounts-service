from accounts.dependencies.database.provider import Storage
from accounts.dependencies.sendgrid.provider import SendGrid


class ServiceMixin:
    name = "accounts"

    storage = Storage()
    sendgrid = SendGrid()

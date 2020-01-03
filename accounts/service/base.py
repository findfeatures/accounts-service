from accounts.dependencies.database.provider import Storage
from accounts.dependencies.redis.provider import Redis
from accounts.dependencies.send_grid.provider import SendGrid
from accounts.dependencies.stripe.provider import Stripe


class ServiceMixin:
    name = "accounts"

    storage = Storage()
    send_grid = SendGrid()
    stripe = Stripe()
    redis = Redis()

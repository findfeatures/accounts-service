from users.service.health_check import HealthCheckServiceMixin
from users.service.users import UsersServiceMixin


class UsersService(HealthCheckServiceMixin, UsersServiceMixin):
    pass

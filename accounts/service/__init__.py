from accounts.service.health_check import HealthCheckServiceMixin
from accounts.service.users import UsersServiceMixin


class AccountsService(HealthCheckServiceMixin, UsersServiceMixin):
    pass

from accounts.service.health_check import HealthCheckServiceMixin
from accounts.service.projects import ProjectsServiceMixin
from accounts.service.stripe import StripeServiceMixin
from accounts.service.users import UsersServiceMixin


class AccountsService(
    HealthCheckServiceMixin, ProjectsServiceMixin, UsersServiceMixin, StripeServiceMixin
):
    pass

import datetime
import logging
from functools import wraps


logger = logging.getLogger(__name__)


def log_entrypoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            f"[{datetime.datetime.utcnow().isoformat()}]: Calling {func.__name__}!"
        )

        return func(*args, **kwargs)

    return wrapper


def sa_to_dict(sensitive_fields=None):
    """
    SQLAlchemy to dictionary function that
    removes the rubbish that sqlalchemy puts into
    the __dict__

    sensitive_fields is a list of strings that shouldn't be returned
    (for example a "password" field)
    """

    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            return _sa_to_dict(result, sensitive_fields=sensitive_fields)

        return wrapper

    return actual_decorator


def _sa_to_dict(result, sensitive_fields=None):
    result_dict = result.__dict__.copy()
    result_dict.pop("_sa_instance_state", None)

    if sensitive_fields:
        for sensitive_field in sensitive_fields:
            result_dict.pop(sensitive_field, None)

    return result_dict


def generate_token(uuid):
    return f"FF.{uuid}"

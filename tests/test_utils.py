from mock import Mock
from users.utils import generate_token, log_entrypoint, sa_to_dict


def test_log_entrypoint_calls_function():
    func = Mock()
    func.__name__ = "test_function"

    decorated_func = log_entrypoint(func)
    decorated_func()
    assert func.called


def test_sa_to_dict():
    @sa_to_dict()
    def fake_func():
        class FakeClass:
            pass

        fake_class = FakeClass()
        fake_class._sa_instance_state = "12341231234124124"
        fake_class.key_1 = "value_1"
        fake_class.key_2 = 123

        return fake_class

    result = fake_func()

    assert result == {"key_1": "value_1", "key_2": 123}


def test_sa_to_dict_with_sensitive_fields():
    @sa_to_dict(sensitive_fields=["password", "sensitive"])
    def fake_func():
        class FakeClass:
            pass

        fake_class = FakeClass()
        fake_class._sa_instance_state = "12341231234124124"
        fake_class.key_1 = "value_1"
        fake_class.key_2 = 123
        fake_class.password = "password"
        fake_class.sensitive = "more passwords?"

        return fake_class

    result = fake_func()

    assert result == {"key_1": "value_1", "key_2": 123}


def test_generate_token():
    uuid = "123"

    assert generate_token(uuid) == f"FF.{uuid}"

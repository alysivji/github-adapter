from flask_login.test_client import FlaskLoginClient
import pytest

from busy_beaver.app import create_app


@pytest.fixture(scope="module")
def app():
    """Session-wide test `Flask` application.

    Establish an application context before running the tests.
    """
    app = create_app(testing=True)
    app.test_client_class = FlaskLoginClient
    ctx = app.app_context()
    ctx.push()
    yield app

    ctx.pop()


@pytest.fixture(scope="module")
def client(app):
    """Create Flask test client where we can trigger test requests to app"""
    client = app.test_client()
    yield client


@pytest.fixture(scope="module")
def login_client(app):
    """Create Flask test client where we can trigger test requests to app"""

    def _wrapper(user):
        client = app.test_client(user=user)
        return client

    yield _wrapper


@pytest.fixture(scope="module")
def runner(app):
    """Create Flask CliRunner that can be used to invoke commands"""
    runner = app.test_cli_runner()
    yield runner

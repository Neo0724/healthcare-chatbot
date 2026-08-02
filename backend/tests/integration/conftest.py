import os

from app.mongodb_client import get_database

os.environ["MONGODB_DB"] = "chatbot_test"
import pytest

from app.main import create_app
from app.routes.test_route import create_test_route


@pytest.fixture
def app():
    """Creates and configures a unique app instance for testing."""
    app = create_app()
    create_test_route(app)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    """Provides a standard Flask HTTP test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def socket_client(app):
    """Provides a connected Socket.IO test client."""
    socketio = app.extensions["socketio"]

    sio_client = socketio.test_client(app)

    yield sio_client

    sio_client.disconnect()


@pytest.fixture(autouse=True)
def clean_database_after_test():
    # --- SETUP CODE (Runs BEFORE the test) ---
    # (Optional: do something before the test starts)

    yield  # <--- The test runs here!

    # --- TEARDOWN CODE (Runs AFTER the test finishes) ---
    # This block executes automatically no matter if the test passed or failed
    get_database()["user"].delete_many({})
    get_database()["message"].delete_many({})
    get_database()["issued_refresh_token"].delete_many({})
    get_database()["conversation_history"].delete_many({})
    print("Cleaned up database!")

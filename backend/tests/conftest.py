import pytest
from app.main import create_app
from app.routes.test_route import create_test_route

@pytest.fixture
def client():
    # Initialize the app with testing configurations
    app = create_app()
    create_test_route(app)
    app.config.update({
        "TESTING": True,  # Propagates exceptions to the test runner
    })

    # Yield the Flask test client
    with app.test_client() as client:
        yield client

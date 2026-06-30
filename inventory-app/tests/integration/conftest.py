import os
import pytest

# These map exactly to your docker-compose.yml Postgres container.
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost" # When in GitLab CI, this will be overridden
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "inventory_test"

from app import create_app, db

@pytest.fixture(scope="session")
def app():
    """Creates a real Flask app connected to the live Postgres container."""
    app = create_app()
    app.config["TESTING"] = True
    
    yield app
    
    # Tear down the database completely after all tests finish
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def session(app):
    """Purges the database before every single test to ensure strict isolation."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield db.session

@pytest.fixture
def client(app):
    """Provides the test client."""
    return app.test_client()
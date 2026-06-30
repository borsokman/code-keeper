import os
import pytest

# Default local values that won't override GitLab CI variables
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "billing_test")

from app import create_app, db


@pytest.fixture(scope="session")
def app():
    """Creates a real Flask app connected to the live Postgres billing container."""
    app = create_app()
    app.config["TESTING"] = True

    yield app

    # Tear down the database completely after all tests finish
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def session(app):
    """Purges the billing database before every test."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield db.session


@pytest.fixture
def client(app):
    return app.test_client()

import os
import pytest
import pika

# Force local test configurations before app components load
os.environ["RABBITMQ_HOST"] = "localhost"
os.environ["RABBITMQ_PORT"] = "5672"
os.environ["RABBITMQ_USER"] = "guest"
os.environ["RABBITMQ_PASSWORD"] = "guest"
os.environ["INVENTORY_URL"] = "http://localhost:8080"

from app import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def clear_queue():
    """Fixture to purge the RabbitMQ queue before and after each integration test."""
    # Pull directly from environment variables to guarantee symmetry with the app
    host = os.environ["RABBITMQ_HOST"]
    port = int(os.environ["RABBITMQ_PORT"])
    user = os.environ["RABBITMQ_USER"]
    password = os.environ["RABBITMQ_PASSWORD"]

    credentials = pika.PlainCredentials(user, password)
    params = pika.ConnectionParameters(host=host, port=port, credentials=credentials)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="billing_queue", durable=True)

    # Purge before test execution
    channel.queue_purge(queue="billing_queue")
    yield channel

    # Clean up after test execution
    channel.queue_purge(queue="billing_queue")
    connection.close()

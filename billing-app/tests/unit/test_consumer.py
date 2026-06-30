import json
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.consumer import callback


@pytest.fixture
def mock_app():
    """Creates a decoupled Flask app workspace instance for tests."""
    app = Flask("test_billing_app")
    return app


@pytest.fixture
def mock_pika_components():
    """Mocks RabbitMQ channel and delivery token objects."""
    ch = MagicMock()
    method = MagicMock()
    method.delivery_tag = 999
    properties = MagicMock()
    return ch, method, properties


@patch("app.consumer.db")
def test_callback_success(mock_db, mock_app, mock_pika_components):
    """Verifies that flawless payloads are successfully committed and acknowledged."""
    ch, method, properties = mock_pika_components

    payload = {"user_id": "user_789", "number_of_items": 4, "total_amount": 150.50}
    body = json.dumps(payload).encode("utf-8")

    callback(mock_app, ch, method, properties, body)

    # Assert database tracking functions were fired
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()

    # Assert RabbitMQ message confirmation occurred
    ch.basic_ack.assert_called_with(delivery_tag=999)


@patch("app.consumer.db")
def test_callback_validation_error_drops_poison_message(
    mock_db, mock_app, mock_pika_components
):
    """Verifies that validation failures drop poison messages without infinite loops."""
    ch, method, properties = mock_pika_components

    # Invalid data (negative item counter value)
    payload = {"user_id": "user_789", "number_of_items": -2, "total_amount": 45.00}
    body = json.dumps(payload).encode("utf-8")

    callback(mock_app, ch, method, properties, body)

    # Verify processing bypassed the database entirely
    mock_db.session.add.assert_not_called()

    # Verify message is rejected and requeue is false
    ch.basic_nack.assert_called_with(delivery_tag=999, requeue=False)


@patch("app.consumer.db")
def test_callback_database_error_triggers_requeue(
    mock_db, mock_app, mock_pika_components
):
    """Verifies that target database errors issue rollbacks and request redelivery."""
    ch, method, properties = mock_pika_components

    # Simulate a sudden database crash or target timeout during processing
    mock_db.session.commit.side_effect = Exception("Database connection failure")

    payload = {"user_id": "user_789", "number_of_items": 1, "total_amount": 12.00}
    body = json.dumps(payload).encode("utf-8")

    callback(mock_app, ch, method, properties, body)

    # Verify rollback handler fired
    mock_db.session.rollback.assert_called_once()

    # Verify message is nacked but requeued for a later attempt
    ch.basic_nack.assert_called_with(delivery_tag=999, requeue=True)

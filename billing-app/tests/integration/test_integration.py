import json
from unittest.mock import MagicMock, patch
from app.models import Order
from app.consumer import callback


def test_consumer_process_valid_order_success(app, session):
    """Integration Test: Valid RabbitMQ payload saves order to Postgres and issues an ACK."""
    # Arrange
    mock_ch = MagicMock()
    mock_method = MagicMock(delivery_tag=101)
    payload = {"user_id": "user_abc123", "number_of_items": 4, "total_amount": 89.95}
    body = json.dumps(payload).encode("utf-8")

    # Act
    callback(app, mock_ch, mock_method, None, body)

    # Assert: Message must be acknowledged exactly once
    mock_ch.basic_ack.assert_called_once_with(delivery_tag=101)
    mock_ch.basic_nack.assert_not_called()

    # Assert: Data was written and committed to the live database container
    with app.app_context():
        orders = Order.query.all()
        assert len(orders) == 1
        assert orders[0].user_id == "user_abc123"
        assert orders[0].number_of_items == 4
        assert orders[0].total_amount == 89.95


def test_consumer_invalid_payload_drops_poison_message(app, session):
    """Integration Test: Validation failures trigger NACK with requeue=False to kill poison messages."""
    # Arrange
    mock_ch = MagicMock()
    mock_method = MagicMock(delivery_tag=102)
    payload = {
        "user_id": "user_abc123",
        "number_of_items": -5,  # Violates 'number_of_items > 0' validation rule
        "total_amount": 89.95,
    }
    body = json.dumps(payload).encode("utf-8")

    # Act
    callback(app, mock_ch, mock_method, None, body)

    # Assert: Poison messages must be discarded without a retry loop
    mock_ch.basic_nack.assert_called_once_with(delivery_tag=102, requeue=False)
    mock_ch.basic_ack.assert_not_called()

    # Assert: Database must reject insertion
    with app.app_context():
        assert Order.query.count() == 0


def test_consumer_database_error_rolls_back_and_requeues(app, session):
    """Integration Test: Unexpected database errors trigger transaction rollback and message requeue."""
    # Arrange
    mock_ch = MagicMock()
    mock_method = MagicMock(delivery_tag=103)
    payload = {
        "user_id": "user_retry_test",
        "number_of_items": 1,
        "total_amount": 10.00,
    }
    body = json.dumps(payload).encode("utf-8")

    # Act: Force an unexpected database execution failure during commit
    with patch(
        "app.db.session.commit", side_effect=Exception("Database connection dropped")
    ):
        callback(app, mock_ch, mock_method, None, body)

    # Assert: Broken network/infra errors must requeue the message for delivery retry
    mock_ch.basic_nack.assert_called_once_with(delivery_tag=103, requeue=True)
    mock_ch.basic_ack.assert_not_called()

    # Assert: Nothing committed to state
    with app.app_context():
        assert Order.query.count() == 0

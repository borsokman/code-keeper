import json
from unittest.mock import patch, ANY
import requests

# ==========================================
# 1. DOWNSTREAM PROXYING TESTS (/api/movies)
# ==========================================


@patch("app.routes.requests.request")
def test_proxy_movies_endpoint_success(mock_request, client):
    """Integration: Verifies the gateway correctly forwards HTTP requests to downstream services."""
    # Arrange
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps([{"id": 1, "title": "Inception"}]).encode(
        "utf-8"
    )
    mock_response.headers = {
        "Content-Type": "application/json",
        "X-Custom-Header": "InventoryValue",
    }
    mock_request.return_value = mock_response

    # Act
    response = client.get("/api/movies/1")

    # Assert
    assert response.status_code == 200
    assert response.json == [{"id": 1, "title": "Inception"}]
    assert response.headers.get("X-Custom-Header") == "InventoryValue"

    # ANY avoids strict type failures against Flask's ImmutableMultiDict
    mock_request.assert_called_once_with(
        method="GET",
        url="http://localhost:8080/api/movies/1",
        params=ANY,
        json=ANY,
        timeout=10,
    )


# ==========================================
# 2. RABBITMQ PUBLISHER TESTS (/api/billing)
# ==========================================


def test_post_billing_success_publishes_to_rabbitmq(client, clear_queue):
    """Integration: Valid payload returns 202 and puts a valid message in the live broker."""
    payload = {
        "user_id": "  user_gateway_test  ",
        "number_of_items": 3,
        "total_amount": 45.50,
    }

    response = client.post("/api/billing", json=payload)

    assert response.status_code == 202
    assert response.json == {"message": "Message posted"}

    method_frame, header_frame, body = clear_queue.basic_get(
        queue="billing_queue", auto_ack=True
    )

    assert method_frame is not None
    message_data = json.loads(body.decode("utf-8"))

    assert message_data["user_id"] == "user_gateway_test"
    assert message_data["number_of_items"] == 3
    assert message_data["total_amount"] == 45.50


def test_post_billing_validation_failure(client, clear_queue):
    """Integration: Bad properties fail validation and drop execution before reaching RabbitMQ."""
    payload = {"user_id": "user_test", "number_of_items": 3, "total_amount": -10.00}

    response = client.post("/api/billing", json=payload)

    assert response.status_code == 400
    assert "total_amount must be >= 0" in response.json["error"]

    method_frame, _, _ = clear_queue.basic_get(queue="billing_queue", auto_ack=True)
    assert method_frame is None

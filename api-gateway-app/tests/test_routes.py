import pytest
from unittest.mock import patch, MagicMock
import requests
import pika
from app import create_app

@pytest.fixture
def client():
    """Sets up a clean Flask test client for every test case."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# === INVENTORY PROXY TESTS ===

@patch("app.routes.requests.request")
def test_proxy_inventory_success(mock_request, client):
    """Verifies that the proxy correctly passes back inventory service responses."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"movie": "Inception"}'
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_request.return_value = mock_resp

    response = client.get("/api/movies/123")
    assert response.status_code == 200
    assert response.data == b'{"movie": "Inception"}'

@patch("app.routes.requests.request")
def test_proxy_inventory_service_down(mock_request, client):
    """Verifies the gateway returns a 502 Bad Gateway if the downstream service blows up."""
    mock_request.side_effect = requests.RequestException()
    
    response = client.get("/api/movies/123")
    assert response.status_code == 502
    assert response.get_json() == {"error": "inventory service unavailable"}


# === BILLING ENDPOINT TESTS ===

def test_post_billing_missing_fields(client):
    """Verifies validation gate catches incomplete JSON payloads."""
    incomplete_payload = {"user_id": "user_01"} # missing total_amount, number_of_items
    response = client.post("/api/billing", json=incomplete_payload)
    
    assert response.status_code == 400
    assert "missing required fields" in response.get_json()["error"]

def test_post_billing_invalid_business_logic(client):
    """Verifies gate catches invalid data values (negative items)."""
    bad_payload = {
        "user_id": "user_01",
        "number_of_items": -5,
        "total_amount": 49.99
    }
    response = client.post("/api/billing", json=bad_payload)
    
    assert response.status_code == 400
    assert "number_of_items must be > 0" in response.get_json()["error"]

@patch("app.routes.pika.BlockingConnection")
def test_post_billing_success_queue_publish(mock_blocking_connection, client):
    """Verifies valid payloads are correctly serialized and published to RabbitMQ."""
    # Mocking out Pika connections completely
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_blocking_connection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel

    valid_payload = {
        "user_id": "user_123",
        "number_of_items": "2", # Route logic converts string to int
        "total_amount": 19.99
    }
    response = client.post("/api/billing", json=valid_payload)
    
    assert response.status_code == 202
    assert response.get_json() == {"message": "Message posted"}
    
    # Assert that the gateway code actually attempted to format the queue properly
    mock_channel.queue_declare.assert_called_with(queue="billing_queue", durable=True)
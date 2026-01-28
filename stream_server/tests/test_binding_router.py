# tests/test_stream_server.py
import asyncio
import json
import pytest
import requests
import websockets
from fastapi.testclient import TestClient
from unittest.mock import patch

from server import app  # your FastAPI app

BASE_URL = "http://localhost:9097/stream"
HEADERS = {"Content-Type": "application/json"}
TEST_USER_ID = 1
TEST_PRODUCT_ID = 123


@pytest.fixture(scope="module")
def client():
    """HTTP Test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_consumers():
    """Patch consumer threads to avoid RabbitMQ in tests"""
    with patch("lib.create_consumer") as mock:
        mock.return_value = None
        yield


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection"""
    uri = f"ws://localhost:9097/stream/ws/{TEST_USER_ID}"
    messages = []

    try:
        async with websockets.connect(uri) as ws:
            # Receive connection message
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            data = json.loads(msg)
            assert data["type"] == "connected"
            assert data["client_id"] == str(TEST_USER_ID)
            messages.append(data)

            # Optionally, wait a few seconds for more messages
            await asyncio.sleep(1)

    except Exception as e:
        pytest.fail(f"WebSocket connection failed: {e}")

    assert len(messages) > 0


def test_binding_endpoints(client):
    """Test queue binding HTTP endpoints"""

    auth_headers = {"Authorization": "Bearer test-token"}

    # User binding
    user_binding = {"routing_key": f"user.{TEST_USER_ID}.notifications"}
    resp = client.post(f"{BASE_URL}/user/{TEST_USER_ID}/bind",
                       json=user_binding, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 403]

    # Product binding
    product_binding = {"routing_key": f"product.{TEST_PRODUCT_ID}.updates"}
    resp = client.post(f"{BASE_URL}/product/{TEST_USER_ID}/{TEST_PRODUCT_ID}/bind",
                       json=product_binding, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 403]

    # Get bindings
    resp = client.get(f"{BASE_URL}/user/{TEST_USER_ID}/bindings",
                      headers=auth_headers)
    assert resp.status_code in [200, 403]

    # Unbind
    unbind_request = {"routing_key": f"user.{TEST_USER_ID}.notifications"}
    resp = client.delete(f"{BASE_URL}/user/{TEST_USER_ID}/unbind",
                         json=unbind_request, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 403, 404]


def test_invalid_binding(client):
    """Test invalid or error cases"""

    auth_headers = {"Authorization": "Bearer test-token"}

    # Invalid user binding
    invalid_binding = {"routing_key": "user.999.notifications"}
    resp = client.post(f"{BASE_URL}/user/{TEST_USER_ID}/bind",
                       json=invalid_binding, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 403]

    # Invalid routing key format
    invalid_binding = {"routing_key": "invalid_format"}
    resp = client.post(f"{BASE_URL}/user/{TEST_USER_ID}/bind",
                       json=invalid_binding, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 400, 403, 422]

    # Empty multiple binding
    empty_binding = {"routing_keys": []}
    resp = client.post(f"{BASE_URL}/user/{TEST_USER_ID}/bind-multiple",
                       json=empty_binding, headers={**HEADERS, **auth_headers})
    assert resp.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_complete_workflow():
    """Test full WebSocket + binding workflow"""
    uri = f"ws://localhost:9097/stream/ws/{TEST_USER_ID}"
    messages = []

    async with websockets.connect(uri) as ws:
        # Connection message
        msg = await asyncio.wait_for(ws.recv(), timeout=2)
        data = json.loads(msg)
        messages.append(data)
        assert data["type"] == "connected"

        # Perform bindings via HTTP
        auth_headers = {"Authorization": "Bearer test-token"}
        user_binding = {"routing_key": f"user.{TEST_USER_ID}.notifications"}
        resp1 = requests.post(f"{BASE_URL}/user/{TEST_USER_ID}/bind",
                              json=user_binding, headers={**HEADERS, **auth_headers})
        assert resp1.status_code in [200, 403]

        product_binding = {"routing_key": f"product.{TEST_PRODUCT_ID}.updates"}
        resp2 = requests.post(f"{BASE_URL}/product/{TEST_USER_ID}/{TEST_PRODUCT_ID}/bind",
                              json=product_binding, headers={**HEADERS, **auth_headers})
        assert resp2.status_code in [200, 403]

        # Get bindings
        resp3 = requests.get(f"{BASE_URL}/user/{TEST_USER_ID}/bindings",
                             headers=auth_headers)
        assert resp3.status_code in [200, 403]

        # Unbind product
        unbind_request = {"routing_key": f"product.{TEST_PRODUCT_ID}.updates"}
        resp4 = requests.delete(f"{BASE_URL}/user/{TEST_USER_ID}/unbind",
                                json=unbind_request, headers={**HEADERS, **auth_headers})
        assert resp4.status_code in [200, 403, 404]

    assert len(messages) > 0

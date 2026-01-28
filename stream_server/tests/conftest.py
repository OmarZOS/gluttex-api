import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# -------------------------------
# Mock settings before importing app
# -------------------------------
@pytest.fixture(autouse=True, scope="session")
def mock_settings():
    """Patch lib.Settings to avoid pydantic validation errors in tests"""
    with patch("lib.settings") as mock:
        # Provide only attributes your tests need
        mock.BASE_URL = "http://localhost:9097/stream"
        mock.TEST_USER_ID = 1
        mock.TEST_PRODUCT_ID = 123
        yield mock

# -------------------------------
# HTTP client fixture
# -------------------------------
@pytest.fixture(scope="module")
def client():
    """FastAPI test client"""
    from server import app  # import after patching settings
    return TestClient(app)

# -------------------------------
# RabbitMQ consumer mocking
# -------------------------------
@pytest.fixture(autouse=True)
def mock_consumers():
    """Patch RabbitMQ consumers"""
    import lib
    with patch.object(lib, "OptimizedPikaConsumerThread") as MockConsumer:
        instance = MockConsumer.return_value
        instance.start.return_value = None
        instance.stop.return_value = None
        instance._run = AsyncMock()
        yield MockConsumer

# -------------------------------
# Async WebSocket fixture
# -------------------------------
@pytest.fixture
async def websocket_client():
    import websockets
    clients = []

    async def _connect(client_id: int):
        uri = f"ws://localhost:9097/stream/ws/{client_id}"
        ws = await websockets.connect(uri)
        clients.append(ws)
        return ws

    yield _connect

    for ws in clients:
        await ws.close()

# -------------------------------
# Event loop for pytest-asyncio
# -------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

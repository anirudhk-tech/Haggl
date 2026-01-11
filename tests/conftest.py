"""
Haggl Test Configuration

Shared fixtures and configuration for pytest.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# -----------------------------------------------------------------------------
# Event Loop Fixture
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# -----------------------------------------------------------------------------
# FastAPI Test Client
# -----------------------------------------------------------------------------


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a synchronous test client for FastAPI."""
    from src.server import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for FastAPI."""
    from src.server import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# -----------------------------------------------------------------------------
# Mock External Services
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_openai() -> Generator[MagicMock, None, None]:
    """Mock OpenAI API calls."""
    with patch("openai.AsyncOpenAI") as mock:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="Mock response",
                            function_call=None,
                        )
                    )
                ]
            )
        )
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_vapi() -> Generator[MagicMock, None, None]:
    """Mock Vapi API calls."""
    with patch("httpx.AsyncClient.post") as mock:
        mock.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "mock-call-id", "status": "queued"},
        )
        yield mock


@pytest.fixture
def mock_vonage() -> Generator[MagicMock, None, None]:
    """Mock Vonage API calls."""
    with patch("httpx.AsyncClient.post") as mock:
        mock.return_value = MagicMock(
            status_code=202,
            json=lambda: {"message_uuid": "mock-message-uuid"},
        )
        yield mock


@pytest.fixture
def mock_mongodb() -> Generator[MagicMock, None, None]:
    """Mock MongoDB operations."""
    with patch("src.storage.database.get_database") as mock:
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        mock.return_value = mock_db
        yield mock


# -----------------------------------------------------------------------------
# Sample Data Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_order() -> dict[str, Any]:
    """Sample order data for testing."""
    return {
        "order_id": "test-order-123",
        "business_id": "test-business-456",
        "product": "eggs",
        "quantity": 12,
        "unit": "dozen",
        "status": "pending",
    }


@pytest.fixture
def sample_vendor() -> dict[str, Any]:
    """Sample vendor data for testing."""
    return {
        "vendor_id": "test-vendor-789",
        "name": "Farm Fresh Eggs Co",
        "phone": "+15551234567",
        "products": ["eggs", "dairy"],
        "quality_score": 92.0,
        "reliability_score": 88.0,
        "certifications": ["organic", "free-range"],
    }


@pytest.fixture
def sample_business() -> dict[str, Any]:
    """Sample business data for testing."""
    return {
        "business_id": "test-business-456",
        "business_name": "Acme Bakery",
        "business_type": "bakery",
        "location": "Austin, TX",
        "phone": "+15559876543",
        "selected_products": ["eggs", "flour", "butter"],
    }


# -----------------------------------------------------------------------------
# Environment Setup
# -----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("VAPI_API_KEY", "test-vapi-key")
    monkeypatch.setenv("VONAGE_API_KEY", "test-vonage-key")
    monkeypatch.setenv("VONAGE_API_SECRET", "test-vonage-secret")
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DB", "haggl_test")

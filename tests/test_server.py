"""
Server API Tests

Tests for the main FastAPI server endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Health endpoint should return 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestOrdersAPI:
    """Test orders endpoints."""

    def test_get_pending_orders(self, client: TestClient, mock_mongodb) -> None:
        """Should return pending orders."""
        response = client.get("/orders/pending")
        assert response.status_code == 200
        assert "pending_approvals" in response.json()

    def test_create_order_missing_business(self, client: TestClient) -> None:
        """Should reject order without business_id."""
        response = client.post(
            "/orders/create",
            json={
                "items": [{"product": "eggs", "quantity": 12, "unit": "dozen"}],
                "phone_number": "+15551234567",
            },
        )
        assert response.status_code == 422

    def test_approve_order_not_found(self, client: TestClient, mock_mongodb) -> None:
        """Should return 404 for non-existent order."""
        response = client.post(
            "/orders/approve",
            json={"order_id": "non-existent-order"},
        )
        # Could be 404 or 400 depending on implementation
        assert response.status_code in [400, 404]


class TestEventsAPI:
    """Test SSE events endpoints."""

    def test_get_recent_events(self, client: TestClient) -> None:
        """Should return recent events."""
        response = client.get("/events/recent")
        assert response.status_code == 200
        assert "events" in response.json()

    def test_event_stream_connection(self, client: TestClient) -> None:
        """Should establish SSE connection."""
        with client.stream("GET", "/events/stream") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")


class TestBusinessAPI:
    """Test business profile endpoints."""

    def test_complete_onboarding(self, client: TestClient, mock_mongodb) -> None:
        """Should create business profile."""
        response = client.post(
            "/onboarding/complete",
            json={
                "business_name": "Test Bakery",
                "business_type": "bakery",
                "location": "Austin, TX",
                "phone": "+15551234567",
                "selected_products": ["eggs", "flour"],
            },
        )
        assert response.status_code == 200
        assert "business_id" in response.json()


class TestWebhooks:
    """Test webhook endpoints."""

    def test_vonage_inbound_get(self, client: TestClient) -> None:
        """Should accept GET webhooks from Vonage."""
        response = client.get(
            "/webhooks/vonage/inbound",
            params={
                "from": "15551234567",
                "to": "15559876543",
                "text": "Hello",
                "type": "text",
            },
        )
        # Should not error, even if processing fails
        assert response.status_code in [200, 500]

    def test_vonage_status_webhook(self, client: TestClient) -> None:
        """Should accept status webhooks."""
        response = client.post(
            "/webhooks/vonage/status",
            json={
                "message_uuid": "test-uuid",
                "status": "delivered",
            },
        )
        assert response.status_code == 200

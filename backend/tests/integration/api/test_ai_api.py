"""Integration tests for AI API endpoints.

Tests the AI REST API using FastAPI TestClient.
Verifies stub implementation and API contracts (SC-009).
"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.infrastructure.database.session import get_async_session


@pytest.fixture
async def client(async_session):
    """Create async HTTP client with database session override."""

    async def override_get_async_session():
        """Override session dependency to use test session."""
        yield async_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_brand(client):
    """Create a test brand for AI endpoints."""
    payload = {
        "name": "AI Test Brand",
        "slug": "ai-test-brand",
        "description": "Test brand for AI API",
        "theme_config": {"primary_color": "#FF6B6B"},
    }
    response = await client.post("/v1/brands", json=payload)
    return response.json()


@pytest.mark.asyncio
class TestAIStatusAPI:
    """Test AI status endpoint."""

    async def test_get_ai_status(self, client):
        """Test GET /v1/ai/status - returns service status."""
        # Act
        response = await client.get("/v1/ai/status")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model_version"] == "stub-v1.0"
        assert data["is_stub"] is True
        assert "recommendations" in data["features_available"]
        assert "demand_forecast" in data["features_available"]
        assert "user_preferences" in data["features_available"]


@pytest.mark.asyncio
class TestRecommendationsAPI:
    """Test recommendations endpoints."""

    async def test_get_recommendations_by_id(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/recommendations - returns recommendations."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/recommendations"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == test_brand["id"]
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert data["model_version"] == "stub-v1.0"
        assert "generated_at" in data

    async def test_get_recommendations_with_limit(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/recommendations?limit=3."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/recommendations?limit=3"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) <= 3

    async def test_get_recommendations_with_user_id(self, client, test_brand):
        """Test personalized recommendations with user_id parameter."""
        # Arrange
        user_id = "00000000-0000-0000-0000-000000000001"

        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/recommendations?user_id={user_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == test_brand["id"]

    async def test_get_recommendations_brand_not_found(self, client):
        """Test GET /v1/ai/brands/{brand_id}/recommendations - 404 for unknown brand."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/v1/ai/brands/{fake_uuid}/recommendations")

        # Assert
        assert response.status_code == 404

    async def test_get_recommendations_invalid_limit(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/recommendations?limit=100 - invalid limit."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/recommendations?limit=100"
        )

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_get_recommendations_by_slug(self, client, test_brand):
        """Test GET /v1/ai/brands/slug/{slug}/recommendations - by slug."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/slug/{test_brand['slug']}/recommendations"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == test_brand["id"]
        assert isinstance(data["recommendations"], list)

    async def test_get_recommendations_by_slug_not_found(self, client):
        """Test GET /v1/ai/brands/slug/{slug}/recommendations - 404 for unknown slug."""
        # Act
        response = await client.get("/v1/ai/brands/slug/non-existent-slug/recommendations")

        # Assert
        assert response.status_code == 404

    async def test_recommendation_item_structure(self, client, test_brand):
        """Test that recommendation items have correct structure."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/recommendations"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        if len(data["recommendations"]) > 0:
            item = data["recommendations"][0]
            assert "item_id" in item
            assert "item_name" in item
            assert "score" in item
            assert "reason" in item
            # Score should be between 0 and 1
            assert 0 <= item["score"] <= 1


@pytest.mark.asyncio
class TestDemandForecastAPI:
    """Test demand forecast endpoints."""

    async def test_get_demand_forecast(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/demand-forecast."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/demand-forecast"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == test_brand["id"]
        assert "predictions" in data
        assert isinstance(data["predictions"], list)
        assert data["forecast_period_days"] == 7  # Default
        assert data["model_version"] == "stub-v1.0"

    async def test_get_demand_forecast_custom_days(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/demand-forecast?forecast_days=14."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/demand-forecast?forecast_days=14"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["forecast_period_days"] == 14

    async def test_get_demand_forecast_brand_not_found(self, client):
        """Test GET /v1/ai/brands/{brand_id}/demand-forecast - 404 for unknown brand."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/v1/ai/brands/{fake_uuid}/demand-forecast")

        # Assert
        assert response.status_code == 404

    async def test_get_demand_forecast_invalid_days(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/demand-forecast?forecast_days=100."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/demand-forecast?forecast_days=100"
        )

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_demand_prediction_item_structure(self, client, test_brand):
        """Test that demand prediction items have correct structure."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/demand-forecast"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        if len(data["predictions"]) > 0:
            pred = data["predictions"][0]
            assert "item_id" in pred
            assert "item_name" in pred
            assert "predicted_quantity" in pred
            assert "confidence" in pred
            assert "prediction_date" in pred
            # Confidence should be between 0 and 1
            assert 0 <= pred["confidence"] <= 1


@pytest.mark.asyncio
class TestUserPreferencesAPI:
    """Test user preferences endpoints."""

    async def test_get_user_preferences(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/user-preferences."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/user-preferences"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "preferred_categories" in data
        assert "preferred_price_range" in data
        assert "dietary_preferences" in data
        assert "order_frequency" in data

    async def test_get_user_preferences_with_user_id(self, client, test_brand):
        """Test GET /v1/ai/brands/{brand_id}/user-preferences?user_id=xxx."""
        # Arrange
        user_id = "00000000-0000-0000-0000-000000000001"

        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/user-preferences?user_id={user_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id

    async def test_get_user_preferences_brand_not_found(self, client):
        """Test GET /v1/ai/brands/{brand_id}/user-preferences - 404 for unknown brand."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/v1/ai/brands/{fake_uuid}/user-preferences")

        # Assert
        assert response.status_code == 404

    async def test_user_preferences_structure(self, client, test_brand):
        """Test that user preferences have correct structure."""
        # Act
        response = await client.get(
            f"/v1/ai/brands/{test_brand['id']}/user-preferences"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Price range should be a tuple/array of [min, max] or None
        if data["preferred_price_range"] is not None:
            assert isinstance(data["preferred_price_range"], list)
            assert len(data["preferred_price_range"]) == 2

        # Dietary preferences should be a list
        assert isinstance(data["dietary_preferences"], list)

        # Order frequency should be a string descriptor
        assert isinstance(data["order_frequency"], str)

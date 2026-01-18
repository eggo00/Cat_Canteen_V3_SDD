"""Integration tests for Brand API endpoints.

Tests the Brand REST API using FastAPI TestClient.
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


@pytest.mark.asyncio
class TestBrandAPI:
    """Test Brand API endpoints."""

    async def test_create_brand_success(self, client):
        """Test POST /v1/brands - successful brand creation."""
        # Arrange
        payload = {
            "name": "貓咪食堂",
            "slug": "cat-canteen",
            "description": "溫馨的貓咪主題餐廳",
            "theme_config": {
                "primary_color": "#FF6B6B",
                "secondary_color": "#4ECDC4",
                "font_family": "Noto Sans TC",
            },
        }

        # Act
        response = await client.post("/v1/brands", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "貓咪食堂"
        assert data["slug"] == "cat-canteen"
        assert data["theme_config"]["primary_color"] == "#FF6B6B"
        assert data["is_active"] is True

    async def test_create_brand_auto_generate_slug(self, client):
        """Test POST /v1/brands - auto-generate slug from name."""
        # Arrange
        payload = {
            "name": "測試餐廳",
            "theme_config": {
                "primary_color": "#FF6B6B",
            },
        }

        # Act
        response = await client.post("/v1/brands", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "ce-shi-can-ting"

    async def test_create_brand_duplicate_slug(self, client):
        """Test POST /v1/brands - duplicate slug returns 409 Conflict."""
        # Arrange
        payload = {
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_config": {"primary_color": "#000000"},
        }

        # Act - Create first brand
        await client.post("/v1/brands", json=payload)

        # Act - Try to create duplicate
        response = await client.post("/v1/brands", json=payload)

        # Assert
        assert response.status_code == 409
        assert "slug" in response.json()["detail"].lower()

    async def test_create_brand_invalid_theme_color(self, client):
        """Test POST /v1/brands - invalid color format returns 422."""
        # Arrange
        payload = {
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_config": {
                "primary_color": "invalid-color",  # Invalid HEX format
            },
        }

        # Act
        response = await client.post("/v1/brands", json=payload)

        # Assert
        assert response.status_code == 422

    async def test_get_brand_by_slug_success(self, client):
        """Test GET /v1/brands/slug/{slug} - retrieve brand by slug."""
        # Arrange - Create a brand first
        create_payload = {
            "name": "Test Restaurant",
            "slug": "test-restaurant",
            "theme_config": {"primary_color": "#FF0000"},
        }
        create_response = await client.post("/v1/brands", json=create_payload)
        created_id = create_response.json()["id"]

        # Act
        response = await client.get("/v1/brands/slug/test-restaurant")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["slug"] == "test-restaurant"
        assert data["name"] == "Test Restaurant"

    async def test_get_brand_by_slug_not_found(self, client):
        """Test GET /v1/brands/slug/{slug} - non-existent brand returns 404."""
        # Act
        response = await client.get("/v1/brands/slug/non-existent-slug")

        # Assert
        assert response.status_code == 404

    async def test_get_brand_by_id_success(self, client):
        """Test GET /v1/brands/{brand_id} - retrieve brand by ID."""
        # Arrange - Create a brand first
        create_payload = {
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_config": {"primary_color": "#FF0000"},
        }
        create_response = await client.post("/v1/brands", json=create_payload)
        brand_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/v1/brands/{brand_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == brand_id
        assert data["name"] == "Test Brand"

    async def test_get_brand_by_id_not_found(self, client):
        """Test GET /v1/brands/{brand_id} - non-existent brand returns 404."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/v1/brands/{fake_uuid}")

        # Assert
        assert response.status_code == 404

    async def test_list_brands(self, client):
        """Test GET /v1/brands - list all brands."""
        # Arrange - Create multiple brands
        for i in range(3):
            payload = {
                "name": f"Brand {i}",
                "slug": f"brand-{i}",
                "theme_config": {"primary_color": "#FF0000"},
            }
            await client.post("/v1/brands", json=payload)

        # Act
        response = await client.get("/v1/brands")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    async def test_list_brands_active_only(self, client):
        """Test GET /v1/brands?active_only=true - list only active brands."""
        # Arrange - Create one active and one inactive brand
        active_payload = {
            "name": "Active Brand",
            "slug": "active-brand",
            "theme_config": {"primary_color": "#FF0000"},
        }
        active_response = await client.post("/v1/brands", json=active_payload)
        active_id = active_response.json()["id"]

        inactive_payload = {
            "name": "Inactive Brand",
            "slug": "inactive-brand",
            "theme_config": {"primary_color": "#00FF00"},
        }
        inactive_response = await client.post("/v1/brands", json=inactive_payload)
        inactive_id = inactive_response.json()["id"]

        # Deactivate the second brand
        await client.patch(
            f"/v1/brands/{inactive_id}",
            json={"is_active": False}
        )

        # Act
        response = await client.get("/v1/brands?active_only=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        brand_ids = [brand["id"] for brand in data]
        assert active_id in brand_ids
        assert inactive_id not in brand_ids

    async def test_update_brand_success(self, client):
        """Test PATCH /v1/brands/{brand_id} - update brand."""
        # Arrange - Create brand
        create_payload = {
            "name": "Original Name",
            "slug": "original-slug",
            "theme_config": {"primary_color": "#000000"},
        }
        create_response = await client.post("/v1/brands", json=create_payload)
        brand_id = create_response.json()["id"]

        # Act - Update brand
        update_payload = {
            "name": "Updated Name",
            "description": "New description",
            "theme_config": {
                "primary_color": "#FF6B6B",
                "secondary_color": "#4ECDC4",
            }
        }
        response = await client.patch(f"/v1/brands/{brand_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"
        assert data["theme_config"]["primary_color"] == "#FF6B6B"

    async def test_update_brand_not_found(self, client):
        """Test PATCH /v1/brands/{brand_id} - non-existent brand returns 404."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        update_payload = {"name": "New Name"}
        response = await client.patch(f"/v1/brands/{fake_uuid}", json=update_payload)

        # Assert
        assert response.status_code == 404

    async def test_deactivate_brand(self, client):
        """Test PATCH /v1/brands/{brand_id} - deactivate brand."""
        # Arrange - Create brand
        create_payload = {
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_config": {"primary_color": "#000000"},
        }
        create_response = await client.post("/v1/brands", json=create_payload)
        brand_id = create_response.json()["id"]

        # Act - Deactivate
        response = await client.patch(
            f"/v1/brands/{brand_id}",
            json={"is_active": False}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_delete_brand_success(self, client):
        """Test DELETE /v1/brands/{brand_id} - delete brand."""
        # Arrange - Create brand
        create_payload = {
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_config": {"primary_color": "#000000"},
        }
        create_response = await client.post("/v1/brands", json=create_payload)
        brand_id = create_response.json()["id"]

        # Act - Delete
        response = await client.delete(f"/v1/brands/{brand_id}")

        # Assert
        assert response.status_code == 204

        # Verify brand is deleted
        get_response = await client.get(f"/v1/brands/{brand_id}")
        assert get_response.status_code == 404

    async def test_delete_brand_not_found(self, client):
        """Test DELETE /v1/brands/{brand_id} - non-existent brand returns 404."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/v1/brands/{fake_uuid}")

        # Assert
        assert response.status_code == 404

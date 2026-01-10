"""Contract tests for Brand API endpoints.

These tests verify the API contract (request/response format)
according to specs/001-white-label-ordering/contracts/api-summary.md

⚠️ TDD: These tests should FAIL initially until implementation is complete.
"""
import pytest
from httpx import AsyncClient

from src.api.main import app


@pytest.mark.asyncio
class TestBrandAPIContracts:
    """Test Brand API endpoint contracts."""

    async def test_create_brand_success(self, async_session):
        """Test POST /v1/brands - successful brand creation.

        Contract:
        - Request: CreateBrandRequest (name, slug, theme_config)
        - Response: 201 Created with BrandResponse
        - Response includes: id, name, slug, theme_config, is_active
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange
            payload = {
                "name": "貓咪食堂",
                "slug": "cat-canteen",
                "description": "溫馨的貓咪主題餐廳",
                "themeConfig": {
                    "primaryColor": "#FF6B6B",
                    "secondaryColor": "#4ECDC4",
                    "fontFamily": "Noto Sans TC",
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
            assert data["themeConfig"]["primaryColor"] == "#FF6B6B"
            assert data["isActive"] is True

    async def test_create_brand_duplicate_slug(self, async_session):
        """Test POST /v1/brands - duplicate slug returns 409 Conflict."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange
            payload = {
                "name": "Test Brand",
                "slug": "test-brand",
                "themeConfig": {"primaryColor": "#000000"},
            }

            # Act - Create first brand
            await client.post("/v1/brands", json=payload)

            # Act - Try to create duplicate
            response = await client.post("/v1/brands", json=payload)

            # Assert
            assert response.status_code == 409
            assert "slug" in response.json()["detail"].lower()

    async def test_create_brand_invalid_theme_color(self, async_session):
        """Test POST /v1/brands - invalid color format returns 422."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange
            payload = {
                "name": "Test Brand",
                "slug": "test-brand",
                "themeConfig": {
                    "primaryColor": "invalid-color",  # Invalid HEX format
                },
            }

            # Act
            response = await client.post("/v1/brands", json=payload)

            # Assert
            assert response.status_code == 422

    async def test_get_brand_by_slug_success(self, async_session):
        """Test GET /v1/brands/{slug} - retrieve brand by slug.

        Contract:
        - Request: slug in path parameter
        - Response: 200 OK with BrandResponse
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create a brand first
            create_payload = {
                "name": "Test Restaurant",
                "slug": "test-restaurant",
                "themeConfig": {"primaryColor": "#FF0000"},
            }
            create_response = await client.post("/v1/brands", json=create_payload)
            created_id = create_response.json()["id"]

            # Act
            response = await client.get("/v1/brands/test-restaurant")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == created_id
            assert data["slug"] == "test-restaurant"
            assert data["name"] == "Test Restaurant"

    async def test_get_brand_by_slug_not_found(self, async_session):
        """Test GET /v1/brands/{slug} - non-existent brand returns 404."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/v1/brands/non-existent-slug")

            # Assert
            assert response.status_code == 404

    async def test_update_brand_theme_success(self, async_session):
        """Test PUT /v1/brands/{slug}/theme - update brand theme.

        Contract:
        - Request: UpdateBrandThemeRequest with theme_config
        - Response: 200 OK with updated BrandResponse
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand
            create_payload = {
                "name": "Test Brand",
                "slug": "test-brand",
                "themeConfig": {"primaryColor": "#000000"},
            }
            await client.post("/v1/brands", json=create_payload)

            # Act - Update theme
            update_payload = {
                "themeConfig": {
                    "primaryColor": "#FF6B6B",
                    "secondaryColor": "#4ECDC4",
                    "fontFamily": "Arial",
                }
            }
            response = await client.put("/v1/brands/test-brand/theme", json=update_payload)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["themeConfig"]["primaryColor"] == "#FF6B6B"
            assert data["themeConfig"]["secondaryColor"] == "#4ECDC4"

    async def test_update_brand_theme_not_found(self, async_session):
        """Test PUT /v1/brands/{slug}/theme - non-existent brand returns 404."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            update_payload = {"themeConfig": {"primaryColor": "#FF0000"}}
            response = await client.put(
                "/v1/brands/non-existent/theme", json=update_payload
            )

            # Assert
            assert response.status_code == 404

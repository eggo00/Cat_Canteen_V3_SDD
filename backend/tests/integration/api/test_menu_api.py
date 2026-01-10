"""Contract tests for Menu API endpoints.

These tests verify the API contract for menu upload and retrieval.

⚠️ TDD: These tests should FAIL initially until implementation is complete.
"""
import pytest
from httpx import AsyncClient

from src.api.main import app


@pytest.mark.asyncio
class TestMenuAPIContracts:
    """Test Menu API endpoint contracts."""

    async def test_upload_menu_success(self, async_session, sample_menu_data):
        """Test POST /v1/brands/{slug}/menu - successful menu upload.

        Contract:
        - Request: UploadMenuRequest with categories array
        - Response: 201 Created with success message
        - Menu should be stored and retrievable
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand first
            brand_payload = {
                "name": "測試餐廳",
                "slug": "test-restaurant",
                "themeConfig": {"primaryColor": "#FF0000"},
            }
            await client.post("/v1/brands", json=brand_payload)

            # Act - Upload menu
            response = await client.post(
                "/v1/brands/test-restaurant/menu", json=sample_menu_data
            )

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert "message" in data or "success" in data

    async def test_upload_menu_brand_not_found(self, async_session, sample_menu_data):
        """Test POST /v1/brands/{slug}/menu - non-existent brand returns 404."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.post(
                "/v1/brands/non-existent/menu", json=sample_menu_data
            )

            # Assert
            assert response.status_code == 404

    async def test_upload_menu_invalid_format(self, async_session):
        """Test POST /v1/brands/{slug}/menu - invalid menu format returns 422."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand
            brand_payload = {
                "name": "Test Brand",
                "slug": "test-brand",
                "themeConfig": {"primaryColor": "#000000"},
            }
            await client.post("/v1/brands", json=brand_payload)

            # Act - Upload invalid menu (missing required fields)
            invalid_menu = {
                "categories": [
                    {
                        "name": "飲料",
                        # Missing menuItems array
                    }
                ]
            }
            response = await client.post("/v1/brands/test-brand/menu", json=invalid_menu)

            # Assert
            assert response.status_code == 422

    async def test_upload_menu_negative_price(self, async_session):
        """Test POST /v1/brands/{slug}/menu - negative price returns 422."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange
            brand_payload = {
                "name": "Test Brand",
                "slug": "test-brand",
                "themeConfig": {"primaryColor": "#000000"},
            }
            await client.post("/v1/brands", json=brand_payload)

            # Act - Upload menu with negative price
            invalid_menu = {
                "categories": [
                    {
                        "name": "飲料",
                        "menuItems": [
                            {
                                "name": "咖啡",
                                "price": -100.00,  # Negative price
                            }
                        ],
                    }
                ]
            }
            response = await client.post("/v1/brands/test-brand/menu", json=invalid_menu)

            # Assert
            assert response.status_code == 422

    async def test_get_menu_success(self, async_session, sample_menu_data):
        """Test GET /v1/brands/{slug}/menu - retrieve menu for brand.

        Contract:
        - Request: slug in path parameter
        - Response: 200 OK with MenuResponse
        - Response includes: categories with menuItems
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand and upload menu
            brand_payload = {
                "name": "測試餐廳",
                "slug": "test-restaurant",
                "themeConfig": {"primaryColor": "#FF0000"},
            }
            await client.post("/v1/brands", json=brand_payload)
            await client.post("/v1/brands/test-restaurant/menu", json=sample_menu_data)

            # Act - Retrieve menu
            response = await client.get("/v1/brands/test-restaurant/menu")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "categories" in data
            assert len(data["categories"]) > 0

            # Verify first category structure
            first_category = data["categories"][0]
            assert "name" in first_category
            assert "menuItems" in first_category

            # Verify first menu item structure
            if first_category["menuItems"]:
                first_item = first_category["menuItems"][0]
                assert "name" in first_item
                assert "price" in first_item

    async def test_get_menu_brand_not_found(self, async_session):
        """Test GET /v1/brands/{slug}/menu - non-existent brand returns 404."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/v1/brands/non-existent/menu")

            # Assert
            assert response.status_code == 404

    async def test_get_menu_empty_menu(self, async_session):
        """Test GET /v1/brands/{slug}/menu - brand with no menu returns empty categories."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand without menu
            brand_payload = {
                "name": "Empty Restaurant",
                "slug": "empty-restaurant",
                "themeConfig": {"primaryColor": "#000000"},
            }
            await client.post("/v1/brands", json=brand_payload)

            # Act
            response = await client.get("/v1/brands/empty-restaurant/menu")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "categories" in data
            assert len(data["categories"]) == 0

    async def test_update_menu_replaces_existing(self, async_session, sample_menu_data):
        """Test POST /v1/brands/{slug}/menu - uploading new menu replaces old one."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Arrange - Create brand and upload initial menu
            brand_payload = {
                "name": "Test Restaurant",
                "slug": "test-restaurant",
                "themeConfig": {"primaryColor": "#000000"},
            }
            await client.post("/v1/brands", json=brand_payload)
            await client.post("/v1/brands/test-restaurant/menu", json=sample_menu_data)

            # Act - Upload new menu
            new_menu = {
                "categories": [
                    {
                        "name": "主餐",
                        "menuItems": [
                            {
                                "name": "牛排",
                                "price": 500.00,
                            }
                        ],
                    }
                ]
            }
            await client.post("/v1/brands/test-restaurant/menu", json=new_menu)

            # Retrieve and verify
            response = await client.get("/v1/brands/test-restaurant/menu")
            data = response.json()

            # Assert - Should only have the new menu
            assert len(data["categories"]) == 1
            assert data["categories"][0]["name"] == "主餐"

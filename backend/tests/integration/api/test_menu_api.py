"""Integration tests for Menu API endpoints.

Tests the Menu REST API using FastAPI TestClient.
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
async def sample_brand(client):
    """Create a sample brand for testing."""
    payload = {
        "name": "測試餐廳",
        "slug": "test-restaurant",
        "theme_config": {"primary_color": "#FF0000"},
    }
    response = await client.post("/v1/brands", json=payload)
    return response.json()


@pytest.fixture
def sample_menu_data():
    """Sample menu data for testing."""
    return {
        "categories": [
            {
                "name": "飲料",
                "description": "各式飲品",
                "display_order": 1,
                "menu_items": [
                    {
                        "name": "美式咖啡",
                        "description": "香醇美式咖啡",
                        "price": 100.00,
                        "display_order": 1,
                        "customization_options": [
                            {
                                "option_type": "size",
                                "name": "大杯",
                                "price_adjustment": 20.00,
                            }
                        ],
                    },
                    {
                        "name": "拿鐵咖啡",
                        "description": "濃郁拿鐵",
                        "price": 120.00,
                        "display_order": 2,
                    },
                ],
            },
            {
                "name": "甜點",
                "description": "美味甜點",
                "display_order": 2,
                "menu_items": [
                    {
                        "name": "提拉米蘇",
                        "price": 150.00,
                        "display_order": 1,
                    }
                ],
            },
        ]
    }


@pytest.mark.asyncio
class TestMenuAPI:
    """Test Menu API endpoints."""

    async def test_upload_menu_success(self, client, sample_brand, sample_menu_data):
        """Test POST /v1/brands/{brand_id}/menu - successful menu upload."""
        # Act
        response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=sample_menu_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2
        assert data["categories"][0]["name"] == "飲料"
        assert len(data["categories"][0]["menu_items"]) == 2

    async def test_upload_menu_replaces_existing(self, client, sample_brand, sample_menu_data):
        """Test POST /v1/brands/{brand_id}/menu - uploading replaces existing menu."""
        # Arrange - Upload first menu
        await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=sample_menu_data
        )

        # Act - Upload new menu
        new_menu_data = {
            "categories": [
                {
                    "name": "新分類",
                    "display_order": 1,
                    "menu_items": [
                        {
                            "name": "新品項",
                            "price": 200.00,
                            "display_order": 1,
                        }
                    ],
                }
            ]
        }
        response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=new_menu_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "新分類"

        # Verify old data is gone
        get_response = await client.get(f"/v1/brands/{sample_brand['id']}/menu")
        get_data = get_response.json()
        assert len(get_data["categories"]) == 1
        assert get_data["categories"][0]["name"] == "新分類"

    async def test_upload_menu_brand_not_found(self, client, sample_menu_data):
        """Test POST /v1/brands/{brand_id}/menu - non-existent brand returns 404."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/v1/brands/{fake_uuid}/menu",
            json=sample_menu_data
        )

        # Assert
        assert response.status_code == 404

    async def test_upload_menu_invalid_data(self, client, sample_brand):
        """Test POST /v1/brands/{brand_id}/menu - invalid menu data returns 422."""
        # Arrange
        invalid_menu = {
            "categories": [
                {
                    "name": "",  # Empty name - invalid
                    "display_order": 1,
                    "menu_items": [],
                }
            ]
        }

        # Act
        response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=invalid_menu
        )

        # Assert
        assert response.status_code in [400, 422]

    async def test_get_menu_success(self, client, sample_brand, sample_menu_data):
        """Test GET /v1/brands/{brand_id}/menu - retrieve complete menu."""
        # Arrange - Upload menu first
        await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=sample_menu_data
        )

        # Act
        response = await client.get(f"/v1/brands/{sample_brand['id']}/menu")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2
        assert data["categories"][0]["name"] == "飲料"
        assert len(data["categories"][0]["menu_items"]) == 2

    async def test_get_menu_empty(self, client, sample_brand):
        """Test GET /v1/brands/{brand_id}/menu - empty menu returns empty categories."""
        # Act
        response = await client.get(f"/v1/brands/{sample_brand['id']}/menu")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == {"categories": []}

    async def test_get_menu_brand_not_found(self, client):
        """Test GET /v1/brands/{brand_id}/menu - non-existent brand returns 404."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/v1/brands/{fake_uuid}/menu")

        # Assert
        assert response.status_code == 404

    async def test_list_categories(self, client, sample_brand, sample_menu_data):
        """Test GET /v1/brands/{brand_id}/menu/categories - list all categories."""
        # Arrange - Upload menu
        await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=sample_menu_data
        )

        # Act
        response = await client.get(
            f"/v1/brands/{sample_brand['id']}/menu/categories"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "飲料"
        assert data[1]["name"] == "甜點"

    async def test_list_categories_without_items(self, client, sample_brand, sample_menu_data):
        """Test GET /v1/brands/{brand_id}/menu/categories?include_items=false."""
        # Arrange - Upload menu
        await client.post(
            f"/v1/brands/{sample_brand['id']}/menu",
            json=sample_menu_data
        )

        # Act
        response = await client.get(
            f"/v1/brands/{sample_brand['id']}/menu/categories?include_items=false"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["menu_items"] == []

    async def test_create_category_success(self, client, sample_brand):
        """Test POST /v1/brands/{brand_id}/menu/categories - create category."""
        # Arrange
        payload = {
            "name": "新分類",
            "description": "新的分類描述",
            "display_order": 1,
        }

        # Act
        response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu/categories",
            json=payload
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新分類"
        assert data["description"] == "新的分類描述"
        assert "id" in data

    async def test_create_category_brand_not_found(self, client):
        """Test POST /v1/brands/{brand_id}/menu/categories - brand not found."""
        # Arrange
        payload = {
            "name": "Test Category",
            "display_order": 1,
        }

        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            f"/v1/brands/{fake_uuid}/menu/categories",
            json=payload
        )

        # Assert
        assert response.status_code == 404

    async def test_get_category_by_id_success(self, client, sample_brand):
        """Test GET /v1/brands/{brand_id}/menu/categories/{category_id}."""
        # Arrange - Create category
        create_payload = {
            "name": "Test Category",
            "display_order": 1,
        }
        create_response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu/categories",
            json=create_payload
        )
        category_id = create_response.json()["id"]

        # Act
        response = await client.get(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{category_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Test Category"

    async def test_get_category_by_id_not_found(self, client, sample_brand):
        """Test GET /v1/brands/{brand_id}/menu/categories/{category_id} - not found."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{fake_uuid}"
        )

        # Assert
        assert response.status_code == 404

    async def test_update_category_success(self, client, sample_brand):
        """Test PATCH /v1/brands/{brand_id}/menu/categories/{category_id}."""
        # Arrange - Create category
        create_payload = {
            "name": "Original Name",
            "display_order": 1,
        }
        create_response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu/categories",
            json=create_payload
        )
        category_id = create_response.json()["id"]

        # Act - Update category
        update_payload = {
            "name": "Updated Name",
            "description": "New description",
            "display_order": 5,
        }
        response = await client.patch(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{category_id}",
            json=update_payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"
        assert data["display_order"] == 5

    async def test_update_category_not_found(self, client, sample_brand):
        """Test PATCH /v1/brands/{brand_id}/menu/categories/{category_id} - not found."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        update_payload = {"name": "New Name"}
        response = await client.patch(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{fake_uuid}",
            json=update_payload
        )

        # Assert
        assert response.status_code == 404

    async def test_delete_category_success(self, client, sample_brand):
        """Test DELETE /v1/brands/{brand_id}/menu/categories/{category_id}."""
        # Arrange - Create category
        create_payload = {
            "name": "Test Category",
            "display_order": 1,
        }
        create_response = await client.post(
            f"/v1/brands/{sample_brand['id']}/menu/categories",
            json=create_payload
        )
        category_id = create_response.json()["id"]

        # Act - Delete
        response = await client.delete(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{category_id}"
        )

        # Assert
        assert response.status_code == 204

        # Verify category is deleted
        get_response = await client.get(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{category_id}"
        )
        assert get_response.status_code == 404

    async def test_delete_category_not_found(self, client, sample_brand):
        """Test DELETE /v1/brands/{brand_id}/menu/categories/{category_id} - not found."""
        # Act
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(
            f"/v1/brands/{sample_brand['id']}/menu/categories/{fake_uuid}"
        )

        # Assert
        assert response.status_code == 404

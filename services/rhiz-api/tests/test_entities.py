"""Test entity endpoints"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_entity(client: AsyncClient) -> None:
    """Test creating an entity"""
    entity_data = {
        "id": "test_entity_1",
        "type": "person",
        "name": "Test User",
        "bio": "A test user",
    }

    response = await client.post("/api/v1/entities/", json=entity_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test_entity_1"
    assert data["name"] == "Test User"
    assert data["verified"] is False


@pytest.mark.asyncio
async def test_get_entity(client: AsyncClient) -> None:
    """Test getting an entity"""
    # First create
    entity_data = {
        "id": "test_entity_2",
        "type": "person",
        "name": "Another User",
    }
    await client.post("/api/v1/entities/", json=entity_data)

    # Then get
    response = await client.get("/api/v1/entities/test_entity_2")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_entity_2"
    assert data["name"] == "Another User"


@pytest.mark.asyncio
async def test_get_nonexistent_entity(client: AsyncClient) -> None:
    """Test getting a non-existent entity"""
    response = await client.get("/api/v1/entities/nonexistent")
    assert response.status_code == 404


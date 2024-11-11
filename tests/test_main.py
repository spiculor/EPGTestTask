import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_participant():
    async with AsyncClient(app=app, base_url="http://test") as ac:

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johns.doe@example.com",
            "gender": "male",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "password": "password123",
        }
        
        files = {
            "avatar": ("avatar.jpg", open("tests/test_avatar.jpg", "rb"), "image/jpeg")
        }

        response = await ac.post("/api/clients/create", data=data, files=files)

        print(response.json())
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_participants():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
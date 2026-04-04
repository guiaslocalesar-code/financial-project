import pytest
from httpx import AsyncClient
from app.main import app
from app.core.auth import create_jwt_token
from uuid import uuid4

@pytest.mark.asyncio
async def test_auth_me_without_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/auth/me")
    assert response.status_code == 403 # HTTPBearer returns 403 if no credentials

@pytest.mark.asyncio
async def test_dashboard_quotaparte_calculation():
    # Mock user and company
    user_id = str(uuid4())
    company_id = str(uuid4())
    token = create_jwt_token(user_id, [{"company_id": company_id, "role": "owner", "quotaparte": 20.0}])
    
    # We would need to mock the database and the dashboard service to fully test this without a real DB.
    # For now, this is a placeholder to show where the test would go.
    pass

@pytest.mark.asyncio
async def test_login_google_invalid_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/google", json={"google_token": "invalid"})
    assert response.status_code == 401

import pytest
from fastapi.exceptions import  HTTPException
from src.core import settings

@pytest.mark.asyncio
async def test_fail_get_account(guest_client):
    response = await guest_client.get("/api/accounts")
    assert response.status_code == 401, "Could fetch account while not authenticated" 

@pytest.mark.asyncio
async def test_pass_get_account(api_client):
    response = await api_client.get("/api/accounts")
    assert response.status_code == 200, "Could not fetch account"
    
@pytest.mark.asyncio
async def test_fail_create_duplicate_account(guest_client, get_fake):
    response = await guest_client.post("/api/accounts", json={
        "username": settings.TEST_USER,
        "first_name": get_fake.first_name(),
        "last_name": get_fake.last_name(),
        "password": settings.TEST_PASSWORD,
        "password_confirm":settings.TEST_PASSWORD
    })
    assert response.status_code == 409, "Didn't raise 409 conflict when creating duplicate user"
    

@pytest.mark.asyncio
async def test_pass_create_account(guest_client, get_fake):
    response = await guest_client.post("/api/accounts", json={
        "username": get_fake.user_name(),
        "first_name": get_fake.first_name(),
        "last_name": get_fake.last_name(),
        "password": settings.TEST_PASSWORD,
        "password_confirm": settings.TEST_PASSWORD
    })
    assert response.status_code == 200, "Could not create account"
    user = dict(response.json())
    login_response = await guest_client.post("/api/accounts/login", data={
        "username": user.get("username"),
        "password": settings.TEST_PASSWORD
    })
    assert login_response.status_code == 200
    
@pytest.mark.asyncio
async def test_pass_refresh_token(api_client):
    response = await api_client.post("/api/accounts/refresh", data={})
    assert response.status_code == 200, f"{response.json()}"
    
@pytest.mark.asyncio
async def test_fail_refresh_token(guest_client):
    response = await guest_client.post("/api/accounts/refresh", data={})
    assert response.status_code == 401, f"{response.json()}"

@pytest.mark.asyncio 
async def test_fail_create_mcp_token(guest_client):
    response = await guest_client.post("/api/accounts/mcp")
    assert response.status_code == 401, f"{response.json()}"
    
@pytest.mark.asyncio
async def test_pass_create_mcp_token(api_client):
    response = await api_client.post("/api/accounts/mcp", data={})
    assert response.status_code == 200, f"{response.json()}"

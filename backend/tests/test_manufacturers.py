import pytest


@pytest.mark.asyncio
async def test_fail_get_manufacturers(guest_client):
    response = await guest_client.get("/api/manufacturers")
    assert response.status_code == 401, f"{response.json()}"


@pytest.mark.asyncio
async def test_pass_get_manufacturers(api_client):
    response = await api_client.get("/api/manufacturers")
    assert response.status_code == 200, f"{response.json()}"


@pytest.mark.asyncio
async def test_fail_create_manufacturers(guest_client, get_fake):
    response = await guest_client.post("/api/manufacturers", json={
        "name": get_fake.company(),
        "website": get_fake.safe_domain_name()
    })
    assert response.status_code == 401, f"{response.json()}"

import uuid


@pytest.mark.asyncio
async def test_pass_create_manufacturers(api_client):
    """See issue no. 24
    
    https://github.com/Arian-Ott/hyperion/issues/24
    
    Last worked on: Mon Jan  5 05:36:21 PM CET 2026
    
    """
    payload = {
        "name": uuid.uuid4().hex[:7],
        "website": f"https://{uuid.uuid7().hex[:7]}.de"
    }

    _ = await api_client.post("/api/manufacturers", json=payload)
    list_of_manufacturers = await api_client.get("/api/manufacturers")
    manufacturers = list_of_manufacturers.json().get("manufacturers")
    for manufacturer in manufacturers:

        if manufacturer.get("name") == payload["name"] and manufacturer.get("website") == payload["website"]:
            pytest.skip("pass")  # Enforces pytest to pass

    raise RuntimeError("Somehow the Manufacturer was not created.")
            
    

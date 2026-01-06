import pytest


@pytest.mark.asyncio
async def test_fail_create_show(guest_client, get_fake):
    result = await guest_client.post("/api/shows", json={
        "name": get_fake.name()
    })
    assert result.status_code == 401, f"{result.json()}"


@pytest.mark.asyncio
async def test_pass_create_show(api_client, get_fake):
    result = await api_client.post("/api/shows", json={
        "name": get_fake.name()
    })
    assert result.status_code == 200, f"{result.json()}"


@pytest.mark.asyncio
async def test_fail_get_shows(guest_client):
    result = await guest_client.get("/api/shows")
    assert result.status_code == 401, f"{result.json()}"




@pytest.mark.asyncio
async def test_fail_get_show_patch(guest_client, demo_show):
    result = await guest_client.get(f"/api/show/{demo_show.get("id")}/patch")
    assert result.status_code == 401, f"{result.json()}"


@pytest.mark.asyncio
async def test_pass_get_shows(api_client, demo_show):
    result = await api_client.get(f"/api/show/{demo_show.get("id")}/patch")
    assert result.status_code == 200, f"{result.json()}"

import pytest

@pytest.mark.asyncio
async def test_fail_get_fixture_types(guest_client):
    response = await guest_client.get("/api/fixture-types")
    assert response.status_code == 401
    

@pytest.mark.asyncio
async def test_pass_get_fixture_types(api_client, get_hazer):
    print(get_hazer)
    response = await api_client.get("/api/fixture-types")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pass_patch_fixture_to_show(api_client, get_hazer, get_moving_head, demo_show):

    response = await api_client.post("/api/fixture-types", json=,)
    assert response.status_code == 200

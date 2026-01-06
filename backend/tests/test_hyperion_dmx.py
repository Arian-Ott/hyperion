import pytest

@pytest.mark.asyncio
async def test_fail_get_otp_challenge(guest_client):
    response = await guest_client.get("/api/dmx/otp-challenge")
    assert response.status_code == 401, f"{response.json()}"
    

@pytest.mark.asyncio
async def test_pass_get_otp_challenge(api_client, get_fake, guest_client):
    response = await api_client.get("/api/dmx/otp-challenge")
    assert response.status_code == 200, f"{response.json()}"
    otp = response.json()
    add_otp_device = await guest_client.post("/api/dmx/otp-authenticate", json={
        "otp": otp.get("otp"),
        "mac_adress": get_fake.mac_address(),
        "name": get_fake.user_name()
    })
    assert add_otp_device.status_code == 200, f"{response.json()}"
    

    

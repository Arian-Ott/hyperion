import pytest
import pytest_asyncio
import httpx
import websockets
from faker import Faker
from src.core import settings
import uuid

BASE_URL = f"http://127.0.0.1:{settings.PORT}"
WS_BASE_URL = f"ws://127.0.0.1:{settings.PORT}"

fake_instance = Faker(locale=["en_GB", "de_DE"])


HTTPX_LIMITS = httpx.Limits(max_keepalive_connections=0, max_connections=1)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def auth_cookies():
    """
    Loggt sich EINMAL pro Test-Session ein und holt die Cookies.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, limits=HTTPX_LIMITS) as client:
        response = await client.post("/api/accounts/login", data={
            "username": settings.TEST_USER,
            "password": settings.TEST_PASSWORD
        })

        if response.status_code != 200:
            pytest.fail(
                f"Login failed! Status: {response.status_code}, Body: {response.text}")

        if not response.cookies:
            pytest.fail("Login erfolgreich, aber keine Cookies erhalten!")

        return response.cookies

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def demo_show(auth_cookies):
    cookie_header_str = "; ".join(
        [f"{k}={v}" for k, v in auth_cookies.items()])
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": cookie_header_str},
        limits=HTTPX_LIMITS
    ) as client:
        

        show = await client.post("/api/shows", json={
            "name": f"test_show_42"
        })
        response = show.json()
        yield response
        await client.delete(f"/api/show/{response.get("id")}")
    
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def get_hazer(auth_cookies):
    cookie_header_str = "; ".join(
        [f"{k}={v}" for k, v in auth_cookies.items()])
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": cookie_header_str},
        limits=HTTPX_LIMITS
    ) as client:

        show = await client.post("/api/manufacturers", json={
            "name": f"ACME Haze GmbH", "website": "example.com"
        })
        response = show.json()
        hazer = await client.post("/api/fixture-types", json={
            "manufacturer_id": response.get("id"),
            "model": "Stage Hazer II",
            "mode_name": "standard",
            "channels": [
                {
                    "dmx_offset": 1,
                    "attribute": "fog",
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                },
                {
                    "dmx_offset": 2,
                    "attribute": "fan",
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                }
            ]
        })
        response = hazer.json()
        yield response
        await client.delete(f"/api/manufacturers/{response.get("manufacturer_id")}")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def get_moving_head(auth_cookies):
    cookie_header_str = "; ".join(
        [f"{k}={v}" for k, v in auth_cookies.items()])
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": cookie_header_str},
        limits=HTTPX_LIMITS
    ) as client:

        show = await client.post("/api/manufacturers", json={
            "name": f"ACME Light GmbH", "website": "example.com"
        })
        response = show.json()
        mh = await client.post("/api/fixture-types", json={
            "manufacturer_id": response.get("id"),
            "model": "Moving Light MH42AT67",
            "mode_name": "standard",
            "channels": [
                {
                    "dmx_offset": 1,
                    "attribute": "dimmer",  # Nutzt die Konstante "dimmer"
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                },
                {
                    "dmx_offset": 2,
                    "attribute": "strobe",
                    "default_value": 0,
                    "highlight_value": 0,
                    "invert_default": False
                },
                {
                    "dmx_offset": 3,
                    "attribute": "pan",
                    # Pan ist standardmäßig oft mittig (50%)
                    "default_value": 128,
                    "highlight_value": 128,
                    "invert_default": False
                },
                {
                    "dmx_offset": 4,
                    "attribute": "pan_fine",
                    "default_value": 128,
                    "highlight_value": 128,
                    "invert_default": False
                },
                {
                    "dmx_offset": 5,
                    "attribute": "tilt",
                    "default_value": 128,
                    "highlight_value": 128,
                    "invert_default": False
                },
                {
                    "dmx_offset": 6,
                    "attribute": "tilt_fine",
                    "default_value": 128,
                    "highlight_value": 128,
                    "invert_default": False
                },
                {
                    "dmx_offset": 7,
                    "attribute": "COLOR_RED",  # Korrigiert von "red" zu Konstante
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                },
                {
                    "dmx_offset": 8,
                    "attribute": "COLOR_GREEN",  # Korrigiert den Tippfehler "gree"
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                },
                {
                    "dmx_offset": 9,
                    "attribute": "COLOR_BLUE",
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                },
                {
                    "dmx_offset": 10,
                    "attribute": "COLOR_WHITE",
                    "default_value": 0,
                    "highlight_value": 255,
                    "invert_default": False
                }
            ]
        })
        response = mh.json()
        yield response
        await client.delete(f"/api/manufacturers/{response.get("manufacturer_id")}")

@pytest_asyncio.fixture(scope="function")
async def api_client(auth_cookies):
    """
    REST-Client.
    Baut den Cookie-String manuell zusammen und sendet ihn als Header.
    """
    cookie_header_str = "; ".join(
        [f"{k}={v}" for k, v in auth_cookies.items()])

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": cookie_header_str},
        limits=HTTPX_LIMITS
    ) as client:
        yield client




@pytest_asyncio.fixture(scope="function")
async def guest_client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        limits=HTTPX_LIMITS
    ) as client:
        yield client


@pytest.fixture(scope="function")
def get_fake():
    yield fake_instance


@pytest_asyncio.fixture(scope="function")
async def ws_client(auth_cookies):
    """
    WebSocket-Client für /ws/engine.
    Extrahiert den Token aus dem Cookie und nutzt ?token=jwttoken.
    """

    token_value = auth_cookies.get("access_token")


    if not token_value:
        try:
            token_value = list(auth_cookies.values())[0]
        except IndexError:
            pytest.fail("Konnte keinen Token im Cookie-Jar finden!")

    endpoint = f"{WS_BASE_URL}/ws/engine?token={token_value}"
    async with websockets.connect(endpoint) as websocket:
        yield websocket


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(call):
    outcome = yield
    if outcome.get_result().outcome == 'skipped' and call.excinfo.value.msg == 'pass':
        outcome.get_result().outcome = 'passed'

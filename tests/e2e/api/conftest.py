from typing import TYPE_CHECKING
from typing import Iterator

import pytest
from httpx import Client

from clientlib.client import AppClient

if TYPE_CHECKING:
    from app.entities.config import Config


@pytest.fixture(scope="session")
def http_session(
    *,
    config: "Config",
) -> Iterator["Client"]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "example-ca.api_client/1.0",
    }

    with Client(
        headers=headers,
        base_url=config.TEST_URL,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def client(
    *,
    http_session: "Client",
) -> "AppClient":
    app_client = AppClient(
        session=http_session,
    )

    return app_client

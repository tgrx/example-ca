from typing import Iterator

import pytest
from httpx import Client

from app.entities.config import Config
from clientlib.client import AppClient


@pytest.fixture(scope="session")
def http_session(*, config: Config) -> Iterator[Client]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "example-ca.api_client/1.0",
    }

    with Client(base_url=config.TEST_URL, headers=headers) as client:
        yield client


@pytest.fixture(scope="session")
def client(*, http_session: Client) -> AppClient:
    app_client = AppClient(session=http_session)

    return app_client

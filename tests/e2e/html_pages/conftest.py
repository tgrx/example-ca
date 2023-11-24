from typing import Iterator

import pytest
from httpx import Client

from app.entities.config import Config


@pytest.fixture(scope="session")
def web_browser(*, config: Config) -> Iterator[Client]:
    headers = {
        "Accept": "text/html",
        "User-Agent": "example-ca.web_browser/1.0",
    }

    with Client(base_url=config.TEST_URL, headers=headers) as client:
        yield client

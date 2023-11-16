from typing import TYPE_CHECKING
from typing import Iterator

import pytest
from httpx import Client

if TYPE_CHECKING:
    from app.entities.config import Config


@pytest.fixture(scope="session")
def web_browser(
    *,
    config: "Config",
) -> Iterator["Client"]:
    headers = {
        "Accept": "text/html",
        "User-Agent": "example-ca.web_browser/1.0",
    }

    with Client(
        headers=headers,
        base_url=config.TEST_URL,
    ) as client:
        yield client

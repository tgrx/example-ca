import pytest

from app.entities.config import Config


@pytest.fixture(scope="session")
def config() -> "Config":
    return Config()

import pytest
from faker import Faker

from app.entities.config import Config


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def faker() -> Faker:
    russian_faker = Faker(["ru-RU"])
    return russian_faker

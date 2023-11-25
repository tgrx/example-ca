import pytest
from faker import Faker

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def author(
    *,
    faker: Faker,
    author_repo: AuthorRepo,
) -> Author:
    author = author_repo.create(name=faker.name())
    return author

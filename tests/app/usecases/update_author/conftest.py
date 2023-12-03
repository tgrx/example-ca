import pytest
from faker import Faker

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def installed_author(*, author_repo: AuthorRepo, faker: Faker) -> Author:
    name = faker.name()
    author = author_repo.create(name=name)

    return author


@pytest.fixture(scope="function")
def james_joyce(*, author_repo: AuthorRepo) -> Author:
    author = author_repo.create(name="James Joyce")

    return author

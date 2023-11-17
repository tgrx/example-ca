from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from faker import Faker

    from app.entities.interfaces import AuthorRepo
    from app.entities.models import Author


@pytest.fixture(scope="function")
def installed_authors(
    *,
    author_repo: "AuthorRepo",
    faker: "Faker",
) -> list["Author"]:
    names = [faker.name() for _ in "1234"]
    authors = [author_repo.create(name=name) for name in names]

    return authors

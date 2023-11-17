from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from faker import Faker

    from app.entities.interfaces import AuthorRepo
    from app.entities.models import Author


@pytest.fixture(scope="function")
def installed_author(
    *,
    author_repo: "AuthorRepo",
    faker: "Faker",
) -> "Author":
    name = faker.name()
    author = author_repo.create(name=name)

    return author

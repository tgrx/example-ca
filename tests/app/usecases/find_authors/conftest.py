import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def installed_authors(*, author_repo: AuthorRepo) -> list[Author]:
    names = [f"author {n}" for n in "abcd"]
    authors = [author_repo.create(name=name) for name in names]

    return authors

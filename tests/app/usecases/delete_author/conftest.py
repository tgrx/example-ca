import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def installed_authors(*, author_repo: AuthorRepo) -> dict[str, Author]:
    authors = {
        author.name: author
        for author in (
            author_repo.create(name=name)
            for name in [
                "pushkin",
                "pelevin",
            ]
        )
    }

    return authors

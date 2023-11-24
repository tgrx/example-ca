import pytest

from app.entities.models import ID
from app.entities.models import Author
from app.repos.local.author import AuthorRepo


@pytest.fixture(scope="function")
def author_repo() -> AuthorRepo:
    index_authors: dict[ID, Author] = {}
    return AuthorRepo(index_authors=index_authors)

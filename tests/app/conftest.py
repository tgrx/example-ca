import pytest

from app.repos.local.author import AuthorRepo


@pytest.fixture(scope="function")
def author_repo() -> "AuthorRepo":
    return AuthorRepo()

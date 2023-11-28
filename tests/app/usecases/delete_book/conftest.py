import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.entities.models import Book


@pytest.fixture(scope="function")
def james_joyce(*, author_repo: AuthorRepo) -> Author:
    author = author_repo.create(name="James Joyce")
    return author


@pytest.fixture(scope="function")
def ulysses(*, book_repo: BookRepo, james_joyce: Author) -> Book:
    book = book_repo.create(
        author_ids=[james_joyce.author_id],
        title="Ulysses",
    )
    return book


@pytest.fixture(scope="function")
def finnegans_wake(*, book_repo: BookRepo, james_joyce: Author) -> Book:
    book = book_repo.create(
        author_ids=[james_joyce.author_id],
        title="Finnegans Wake",
    )
    return book

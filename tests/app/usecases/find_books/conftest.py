import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.entities.models import Book


@pytest.fixture(scope="function")
def finnegans_wake(book_repo: BookRepo) -> Book:
    title = "Finnegans Wake"
    book = book_repo.create(title=title)
    return book


@pytest.fixture(scope="function")
def james_joyce(
    author_repo: AuthorRepo,
    finnegans_wake: Book,
    ulysses: Book,
) -> Author:
    book_ids = {finnegans_wake.book_id, ulysses.book_id}
    name = "James Joyce"
    author = author_repo.create(book_ids=book_ids, name=name)
    return author


@pytest.fixture(scope="function")
def ulysses(book_repo: BookRepo) -> Book:
    title = "Ulysses"
    book = book_repo.create(title=title)
    return book


__all__ = (
    "finnegans_wake",
    "james_joyce",
    "ulysses",
)

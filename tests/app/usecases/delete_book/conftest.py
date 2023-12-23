import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.entities.models import Book


@pytest.fixture(scope="function")
def bible(book_repo: BookRepo) -> Book:
    title = "Ulysses"
    book = book_repo.create(title=title)
    return book


@pytest.fixture(scope="function")
def laws(book_repo: BookRepo) -> Book:
    title = "Laws"
    book = book_repo.create(title=title)
    return book


@pytest.fixture(scope="function")
def plato(author_repo: AuthorRepo, laws: Book) -> Author:
    book_ids = [laws.book_id]
    name = "Plato"
    author = author_repo.create(book_ids=book_ids, name=name)
    return author


__all__ = (
    "bible",
    "laws",
    "plato",
)

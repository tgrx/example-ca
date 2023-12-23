import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.entities.models import Book


@pytest.fixture(scope="function")
def aristotle(author_repo: AuthorRepo, categoriae: Book) -> Author:
    book_ids = [categoriae.book_id]
    name = "Aristotle"
    author = author_repo.create(book_ids=book_ids, name=name)
    return author


@pytest.fixture(scope="function")
def categoriae(book_repo: BookRepo) -> Book:
    title = "Categoriae"
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


@pytest.fixture(scope="function")
def republic(book_repo: BookRepo) -> Book:
    title = "Republic"
    book = book_repo.create(title=title)
    return book


__all__ = (
    "aristotle",
    "categoriae",
    "laws",
    "plato",
    "republic",
)

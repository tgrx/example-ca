from typing import NamedTuple

import pytest

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from app.repos.local.author import AuthorRepo
from app.repos.local.book import BookRepo


class Indices(NamedTuple):
    authors: dict[ID, Author]
    books: dict[ID, Book]


@pytest.fixture(scope="function")
def indices() -> Indices:
    return Indices(authors={}, books={})


@pytest.fixture(scope="function")
def author_repo(*, indices: Indices) -> AuthorRepo:
    return AuthorRepo(index_authors=indices.authors)


@pytest.fixture(scope="function")
def book_repo(*, indices: Indices) -> BookRepo:
    return BookRepo(index_authors=indices.authors, index_books=indices.books)

from typing import NamedTuple

import pytest

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from app.repos.local.author import AuthorRepo
from app.repos.local.book import BookRepo


class Indices(NamedTuple):
    authors: dict[ID, Author]
    books_authors: dict[ID, set[ID]]
    books: dict[ID, Book]


@pytest.fixture(scope="function")
def indices() -> Indices:
    return Indices(authors={}, books_authors={}, books={})


@pytest.fixture(scope="function")
def author_repo(indices: Indices) -> AuthorRepo:
    return AuthorRepo(
        index_authors=indices.authors,
        index_books_authors=indices.books_authors,
        index_books=indices.books,
    )


@pytest.fixture(scope="function")
def book_repo(indices: Indices) -> BookRepo:
    return BookRepo(
        index_authors=indices.authors,
        index_books_authors=indices.books_authors,
        index_books=indices.books,
    )


__all__ = (
    "author_repo",
    "book_repo",
)

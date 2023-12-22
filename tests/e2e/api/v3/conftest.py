from typing import Iterable

import pytest
from sqlalchemy import Engine

from app.entities.models import Author
from app.entities.models import Book
from app.repos.sqlalchemy.author import AuthorRepo
from app.repos.sqlalchemy.book import BookRepo


@pytest.fixture(scope="function")
def tales(primary_database_engine: Engine) -> Iterable[Book]:
    repo = BookRepo(engine=primary_database_engine)

    book = repo.create(title="Kinder- und Hausmärchen")

    yield book

    repo.delete(book.book_id)


@pytest.fixture(scope="function")
def grimm_jacob(
    primary_database_engine: Engine,
    tales: Book,
) -> Iterable[Author]:
    repo = AuthorRepo(engine=primary_database_engine)

    author = repo.create(name="Jacob Grimm", book_ids=[tales.book_id])

    yield author

    repo.delete(author.author_id)


@pytest.fixture(scope="function")
def grimm_wilhelm(
    primary_database_engine: Engine,
    tales: Book,
) -> Iterable[Author]:
    repo = AuthorRepo(engine=primary_database_engine)

    author = repo.create(name="Wilhelm Grimm", book_ids=[tales.book_id])

    yield author

    repo.delete(author.author_id)

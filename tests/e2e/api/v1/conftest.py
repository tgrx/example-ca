from typing import Iterable

import pytest
from sqlalchemy import Engine

from app.entities.models import Author
from app.entities.models import Book
from app.repos.sqlalchemy.author import AuthorRepo
from app.repos.sqlalchemy.book import BookRepo


@pytest.fixture(scope="function")
def james_joyce(
    primary_database_engine: Engine,
    ulysses: Book,
) -> Iterable[Author]:
    repo = AuthorRepo(engine=primary_database_engine)

    author = repo.create(book_ids=[ulysses.book_id], name="James Joyce")

    yield author

    repo.delete(author.author_id)


@pytest.fixture(scope="function")
def numbers(primary_database_engine: Engine) -> Iterable[Book]:
    repo = BookRepo(engine=primary_database_engine)

    book = repo.create(title="Numbers")

    yield book

    repo.delete(book.book_id)


@pytest.fixture(scope="function")
def ulysses(primary_database_engine: Engine) -> Iterable[Book]:
    repo = BookRepo(engine=primary_database_engine)

    book = repo.create(title="Ulysses")

    yield book

    repo.delete(book.book_id)


@pytest.fixture(scope="function")
def victor_pelevin(
    primary_database_engine: Engine,
    numbers: Book,
) -> Iterable[Author]:
    repo = AuthorRepo(engine=primary_database_engine)

    author = repo.create(book_ids=[numbers.book_id], name="Victor Pelevin")

    yield author

    repo.delete(author.author_id)

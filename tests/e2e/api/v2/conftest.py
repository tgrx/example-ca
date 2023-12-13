from typing import Iterable

import pytest
from sqlalchemy import Engine

from app.entities.models import Book
from app.repos.sqlalchemy.book import BookRepo


@pytest.fixture(scope="function")
def laws(primary_database_engine: Engine) -> Iterable[Book]:
    repo = BookRepo(engine=primary_database_engine)

    book = repo.create(title="Laws")

    yield book

    repo.delete(book.book_id)

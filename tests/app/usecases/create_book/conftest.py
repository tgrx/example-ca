import pytest

from app.entities.interfaces import BookRepo
from app.entities.models import Book


@pytest.fixture(scope="function")
def bible(
    book_repo: BookRepo,
) -> Book:
    title = "Bible"
    book = book_repo.create(title=title)
    return book


__all__ = ("bible",)

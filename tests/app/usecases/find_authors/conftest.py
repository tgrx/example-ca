import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.entities.models import Book


@pytest.fixture(scope="function")
def grimm_jacob(author_repo: AuthorRepo, tales: Book) -> Author:
    book_ids = [tales.book_id]
    name = "Jacob Grimm"
    author = author_repo.create(book_ids=book_ids, name=name)
    return author


@pytest.fixture(scope="function")
def grimm_wilhelm(author_repo: AuthorRepo, tales: Book) -> Author:
    book_ids = [tales.book_id]
    name = "Wilhelm Grimm"
    author = author_repo.create(book_ids=book_ids, name=name)
    return author


@pytest.fixture(scope="function")
def tales(book_repo: BookRepo) -> Book:
    title = "Tales"
    book = book_repo.create(title=title)
    return book


__all__ = (
    "grimm_jacob",
    "grimm_wilhelm",
    "tales",
)

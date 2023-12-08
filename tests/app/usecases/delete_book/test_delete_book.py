from uuid import uuid4

import pytest

from app.entities.errors import DegenerateAuthorsError
from app.entities.models import Author
from app.entities.models import Book
from app.usecases.book import DeleteBookUseCase


@pytest.mark.unit
def test_correct_delete(
    bible: Book,
    delete_book: DeleteBookUseCase,
) -> None:
    delete_book(bible.book_id)


@pytest.mark.unit
def test_deny_degenerate_authors(
    delete_book: DeleteBookUseCase,
    laws: Book,
    plato: Author,
) -> None:
    with pytest.raises(DegenerateAuthorsError) as excinfo:
        delete_book(laws.book_id)

    assert excinfo.value.errors == [f"{plato.name}"]


@pytest.mark.unit
def test_lost_delete(
    delete_book: DeleteBookUseCase,
) -> None:
    book_id = uuid4()
    delete_book(book_id)


@pytest.mark.unit
def test_noop_delete(
    bible: Book,
    delete_book: DeleteBookUseCase,
) -> None:
    delete_book(bible.book_id)
    delete_book(bible.book_id)


__all__ = (
    "test_correct_delete",
    "test_deny_degenerate_authors",
    "test_lost_delete",
    "test_noop_delete",
)

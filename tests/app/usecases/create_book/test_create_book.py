import pytest

from app.entities.errors import DuplicateBookTitleError
from app.entities.models import Book
from app.usecases.book import CreateBookUseCase


@pytest.mark.unit
def test_correct_create(
    create_book: CreateBookUseCase,
) -> None:
    title = "Bible"
    book = create_book(title=title)
    assert book.book_id
    assert book.authors == []
    assert book.title == title


@pytest.mark.unit
def test_require_unique_title(
    bible: Book,
    create_book: CreateBookUseCase,
) -> None:
    with pytest.raises(DuplicateBookTitleError) as excinfo:
        create_book(title=bible.title)

    assert excinfo.value.errors == [f"dup book {bible.title!r}"]


__all__ = (
    "test_correct_create",
    "test_require_unique_title",
)

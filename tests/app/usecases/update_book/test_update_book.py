from uuid import uuid4

import pytest
from faker import Faker

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostBookError
from app.entities.models import Author
from app.entities.models import Book
from app.usecases.book import UpdateBookUseCase


@pytest.mark.unit
def test_correct_update_authors(
    republic: Book,
    plato: Author,
    update_book: UpdateBookUseCase,
) -> None:
    assert republic.authors == ()
    authors = (plato,)
    author_ids = {a.author_id for a in authors}
    book = update_book(republic.book_id, author_ids=author_ids)
    assert book.authors != republic.authors
    assert book.authors == authors
    assert book.book_id == republic.book_id
    assert book.title == republic.title


@pytest.mark.unit
def test_correct_update_title(
    laws: Book,
    update_book: UpdateBookUseCase,
) -> None:
    title = "Νόμοι"
    book = update_book(laws.book_id, title=title)
    assert book.authors == laws.authors
    assert book.book_id == laws.book_id
    assert book.title != laws.title
    assert book.title == title


@pytest.mark.unit
def test_deny_degenerate_author(
    laws: Book,
    plato: Author,
    update_book: UpdateBookUseCase,
) -> None:
    with pytest.raises(DegenerateAuthorsError) as excinfo:
        update_book(laws.book_id, author_ids=[])

    assert excinfo.value.errors == [
        f"The Author(author_id={plato.author_id}, name={plato.name!r})"
        " will become degenerate without books."
    ]


@pytest.mark.unit
def test_deny_lost(
    faker: Faker,
    update_book: UpdateBookUseCase,
) -> None:
    lost_book_id = uuid4()
    lost_title = faker.job()

    with pytest.raises(LostBookError) as excinfo:
        update_book(lost_book_id, title=lost_title)

    assert excinfo.value.errors == [
        f"The Book(book_id={lost_book_id}) does not exist."
    ]


@pytest.mark.unit
def test_noop_update(
    laws: Book,
    update_book: UpdateBookUseCase,
) -> None:
    book = update_book(laws.book_id, title=laws.title)
    assert book == laws


@pytest.mark.unit
def test_require_unique_name(
    laws: Book,
    republic: Book,
    update_book: UpdateBookUseCase,
) -> None:
    with pytest.raises(DuplicateBookTitleError) as excinfo:
        update_book(laws.book_id, title=republic.title)

    assert excinfo.value.errors == [
        f"The Book(title={republic.title!r}) already exists."
    ]


__all__ = (
    "test_correct_update_authors",
    "test_correct_update_title",
    "test_deny_lost",
    "test_noop_update",
    "test_require_unique_name",
)

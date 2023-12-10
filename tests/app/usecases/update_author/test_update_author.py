from uuid import uuid4

import pytest
from faker import Faker

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateAuthorNameError
from app.entities.errors import LostAuthorsError
from app.entities.models import Author
from app.entities.models import Book
from app.usecases.author import UpdateAuthorUseCase


@pytest.mark.unit
def test_correct_update_books(
    laws: Book,
    plato: Author,
    republic: Book,
    update_author: UpdateAuthorUseCase,
) -> None:
    assert plato.book_ids == [laws.book_id]

    books = [laws, republic]
    book_ids = [b.book_id for b in books]
    author = update_author(plato.author_id, book_ids=book_ids)

    assert author.author_id == plato.author_id
    assert author.book_ids == book_ids
    assert author.name == plato.name


@pytest.mark.unit
def test_correct_update_name(
    plato: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    name = "Aristocles"
    author = update_author(plato.author_id, name=name)

    assert author.author_id == plato.author_id
    assert author.book_ids == plato.book_ids
    assert author.name != plato.name
    assert author.name == name


@pytest.mark.unit
def test_deny_degenerate_author(
    plato: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    with pytest.raises(DegenerateAuthorsError) as excinfo:
        update_author(plato.author_id, book_ids=[])

    assert excinfo.value.errors == [
        f"The Author(author_id={plato.author_id}, name={plato.name!r})"
        " will become degenerate without books."
    ]


@pytest.mark.unit
def test_deny_lost(
    faker: Faker,
    update_author: UpdateAuthorUseCase,
) -> None:
    lost_author_id = uuid4()
    lost_name = faker.name()

    with pytest.raises(LostAuthorsError) as excinfo:
        update_author(lost_author_id, name=lost_name)

    assert excinfo.value.errors == [
        f"The Author(author_id={lost_author_id}) does not exist."
    ]


@pytest.mark.unit
def test_noop_update(
    plato: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    author = update_author(
        plato.author_id,
        book_ids=plato.book_ids,
        name=plato.name,
    )

    assert author == plato


@pytest.mark.unit
def test_require_unique_name(
    aristotle: Author,
    plato: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    with pytest.raises(DuplicateAuthorNameError) as excinfo:
        update_author(plato.author_id, name=aristotle.name)

    assert excinfo.value.errors == [
        f"The Author(name={aristotle.name!r}) already exists."
    ]


__all__ = (
    "test_correct_update_books",
    "test_correct_update_name",
    "test_deny_degenerate_author",
    "test_deny_lost",
    "test_noop_update",
    "test_require_unique_name",
)

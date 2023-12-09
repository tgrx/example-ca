import pytest
from faker import Faker

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateAuthorNameError
from app.entities.models import Author
from app.entities.models import Book
from app.usecases.author import CreateAuthorUseCase


@pytest.mark.unit
def test_correct_create(
    create_author: CreateAuthorUseCase,
    laws: Book,
) -> None:
    name = "Plato"
    plato = create_author(book_ids=[laws.book_id], name=name)
    assert plato.author_id
    assert plato.books == (laws,)
    assert plato.name == name


@pytest.mark.unit
def test_deny_degenerate_authors(
    create_author: CreateAuthorUseCase,
    faker: Faker,
) -> None:
    name = faker.name()
    with pytest.raises(DegenerateAuthorsError) as excinfo:
        create_author(book_ids=[], name=name)

    assert excinfo.value.errors == [
        f"The Author({name=!r}) will become degenerate without books."
    ]


@pytest.mark.unit
def test_require_unique_name(
    create_author: CreateAuthorUseCase,
    laws: Book,
    plato: Author,
) -> None:
    with pytest.raises(DuplicateAuthorNameError) as excinfo:
        create_author(book_ids=[laws.book_id], name=plato.name)

    assert excinfo.value.errors == [
        f"The Author(name={plato.name!r}) already exists."
    ]


__all__ = (
    "test_correct_create",
    "test_deny_degenerate_authors",
    "test_require_unique_name",
)

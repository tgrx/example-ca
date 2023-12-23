from uuid import uuid4

import pytest

from app.entities.models import Author
from app.usecases.author import DeleteAuthorUseCase


@pytest.mark.unit
def test_correct_delete(
    delete_author: DeleteAuthorUseCase,
    plato: Author,
) -> None:
    delete_author(plato.author_id)


@pytest.mark.unit
def test_lost_delete(
    delete_author: DeleteAuthorUseCase,
) -> None:
    author_id = uuid4()
    delete_author(author_id)


@pytest.mark.unit
def test_noop_delete(
    delete_author: DeleteAuthorUseCase,
    plato: Author,
) -> None:
    delete_author(plato.author_id)
    delete_author(plato.author_id)


__all__ = (
    "test_correct_delete",
    "test_lost_delete",
    "test_noop_delete",
)

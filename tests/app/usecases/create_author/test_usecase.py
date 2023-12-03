import pytest
from faker import Faker

from app.entities.errors import DuplicateAuthorError
from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import CreateAuthorUseCase


@pytest.mark.unit
def test_happy(
    *,
    author_repo: AuthorRepo,
    create_author: CreateAuthorUseCase,
    faker: Faker,
) -> None:
    name = faker.name()
    author = create_author(name=name)

    assert author.author_id
    assert author.name == name

    authors = author_repo.get_all()
    assert author in authors


@pytest.mark.unit
def test_duplicate_author(
    *,
    existing_author: Author,
    create_author: CreateAuthorUseCase,
) -> None:
    with pytest.raises(DuplicateAuthorError):
        create_author(name=existing_author.name)

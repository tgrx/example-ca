import pytest
from faker import Faker

from app.entities.errors import DuplicateAuthorError
from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import UpdateAuthorUseCase


@pytest.mark.unit
def test_happy(
    *,
    author_repo: AuthorRepo,
    faker: Faker,
    installed_author: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    name = faker.name()
    author = update_author(installed_author.author_id, name=name)

    assert author.author_id == installed_author.author_id
    assert author.name != installed_author.name
    assert author.name == name

    authors = author_repo.get_all()
    assert author in authors


@pytest.mark.unit
def test_duplicate_author(
    *,
    author_repo: AuthorRepo,
    installed_author: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    authors_begin = author_repo.get_all()

    with pytest.raises(DuplicateAuthorError):
        update_author(installed_author.author_id, name=installed_author.name)

    authors_end = author_repo.get_all()
    assert authors_begin == authors_end

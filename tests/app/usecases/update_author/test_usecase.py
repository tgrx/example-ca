from uuid import uuid4

import pytest
from faker import Faker

from app.entities.errors import DuplicateAuthorNameError
from app.entities.errors import LostAuthorError
from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import UpdateAuthorUseCase


@pytest.mark.unit
def test_update_new_name(
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
def test_update_same_name(
    *,
    author_repo: AuthorRepo,
    installed_author: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    authors_begin = author_repo.get_all()

    author = update_author(
        installed_author.author_id,
        name=installed_author.name,
    )
    assert author == installed_author

    authors_end = author_repo.get_all()
    assert authors_begin == authors_end


@pytest.mark.unit
def test_update_taken_name(
    *,
    author_repo: AuthorRepo,
    installed_author: Author,
    james_joyce: Author,
    update_author: UpdateAuthorUseCase,
) -> None:
    authors_begin = author_repo.get_all()

    with pytest.raises(DuplicateAuthorNameError):
        update_author(installed_author.author_id, name=james_joyce.name)

    authors_end = author_repo.get_all()
    assert authors_begin == authors_end


@pytest.mark.unit
def test_update_lost_author(
    *,
    author_repo: AuthorRepo,
    faker: Faker,
    update_author: UpdateAuthorUseCase,
) -> None:
    lost_author_id = uuid4()
    assert author_repo.get_by_id(lost_author_id) is None

    with pytest.raises(LostAuthorError):
        update_author(lost_author_id, name=faker.name())

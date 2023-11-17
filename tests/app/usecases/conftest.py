from typing import TYPE_CHECKING

import pytest

from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import FindAuthorsUseCase
from app.usecases.author import GetAllAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase

if TYPE_CHECKING:
    from app.entities.interfaces import AuthorRepo


@pytest.fixture(scope="function")
def create_author(
    *,
    author_repo: "AuthorRepo",
) -> "CreateAuthorUseCase":
    return CreateAuthorUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def find_authors(
    *,
    author_repo: "AuthorRepo",
) -> "FindAuthorsUseCase":
    return FindAuthorsUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def get_all_authors(
    *,
    author_repo: "AuthorRepo",
) -> "GetAllAuthorsUseCase":
    return GetAllAuthorsUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def update_author(
    *,
    author_repo: "AuthorRepo",
) -> "UpdateAuthorUseCase":
    return UpdateAuthorUseCase(repo=author_repo)

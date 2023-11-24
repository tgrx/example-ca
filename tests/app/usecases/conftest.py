import pytest

from app.entities.interfaces import AuthorRepo
from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import FindAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase


@pytest.fixture(scope="function")
def create_author(*, author_repo: AuthorRepo) -> CreateAuthorUseCase:
    return CreateAuthorUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def find_authors(*, author_repo: AuthorRepo) -> FindAuthorsUseCase:
    return FindAuthorsUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def update_author(*, author_repo: AuthorRepo) -> UpdateAuthorUseCase:
    return UpdateAuthorUseCase(repo=author_repo)

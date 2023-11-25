import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.interfaces import BookRepo
from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import DeleteAuthorUseCase
from app.usecases.author import FindAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase
from app.usecases.book import CreateBookUseCase
from app.usecases.book import DeleteBookUseCase
from app.usecases.book import FindBooksUseCase
from app.usecases.book import UpdateBookUseCase


@pytest.fixture(scope="function")
def create_author(*, author_repo: AuthorRepo) -> CreateAuthorUseCase:
    return CreateAuthorUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def delete_author(*, author_repo: AuthorRepo) -> DeleteAuthorUseCase:
    return DeleteAuthorUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def find_authors(*, author_repo: AuthorRepo) -> FindAuthorsUseCase:
    return FindAuthorsUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def update_author(*, author_repo: AuthorRepo) -> UpdateAuthorUseCase:
    return UpdateAuthorUseCase(repo=author_repo)


@pytest.fixture(scope="function")
def create_book(*, book_repo: BookRepo) -> CreateBookUseCase:
    return CreateBookUseCase(repo=book_repo)


@pytest.fixture(scope="function")
def delete_book(*, book_repo: BookRepo) -> DeleteBookUseCase:
    return DeleteBookUseCase(repo=book_repo)


@pytest.fixture(scope="function")
def find_books(*, book_repo: BookRepo) -> FindBooksUseCase:
    return FindBooksUseCase(repo=book_repo)


@pytest.fixture(scope="function")
def update_book(*, book_repo: BookRepo) -> UpdateBookUseCase:
    return UpdateBookUseCase(repo=book_repo)

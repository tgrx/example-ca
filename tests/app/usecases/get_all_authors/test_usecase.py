from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.interfaces import AuthorRepo
    from app.entities.models import Author
    from app.usecases.author import GetAllAuthorsUseCase


def test_usecase(
    *,
    author_repo: "AuthorRepo",
    get_all_authors: "GetAllAuthorsUseCase",
    installed_authors: list["Author"],
) -> None:
    authors = get_all_authors()

    assert authors == installed_authors
    assert authors == author_repo.get_all()

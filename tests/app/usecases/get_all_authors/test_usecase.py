from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import GetAllAuthorsUseCase


def test_usecase(
    *,
    authors: list["Author"],
    repo: "AuthorRepo",
) -> None:
    get_all_authors = GetAllAuthorsUseCase(repo=repo)

    got_authors = get_all_authors()

    assert got_authors == authors

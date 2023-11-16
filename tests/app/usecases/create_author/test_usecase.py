import os

from app.entities.interfaces import AuthorRepo
from app.usecases.author import CreateAuthorUseCase


def test_usecase(
    *,
    repo: "AuthorRepo",
) -> None:
    create_author = CreateAuthorUseCase(repo=repo)

    salt = os.urandom(4).hex()
    name = f"test name {salt}"
    author = create_author(name=name)

    assert author.id
    assert author.name == name

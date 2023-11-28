from faker import Faker

from app.entities.interfaces import AuthorRepo
from app.usecases.author import CreateAuthorUseCase


def test_usecase(
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

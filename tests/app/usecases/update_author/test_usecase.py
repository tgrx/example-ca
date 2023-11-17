from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from faker import Faker

    from app.entities.interfaces import AuthorRepo
    from app.entities.models import Author
    from app.usecases.author import UpdateAuthorUseCase


def test_usecase(
    *,
    author_repo: "AuthorRepo",
    faker: "Faker",
    installed_author: "Author",
    update_author: "UpdateAuthorUseCase",
) -> None:
    name = faker.name()
    author = update_author(id=installed_author.id, name=name)

    assert author.id == installed_author.id
    assert author.name != installed_author.name
    assert author.name == name

    authors = author_repo.get_all()
    assert author in authors

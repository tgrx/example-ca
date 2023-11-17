from typing import TYPE_CHECKING
from typing import Generator
from uuid import UUID

import attrs

if TYPE_CHECKING:
    from app.entities.interfaces import AuthorRepo
    from app.entities.models import Author


@attrs.frozen(kw_only=True, slots=True)
class GetAllAuthorsUseCase:
    """
    Use case: Get all authors.
    """

    repo: "AuthorRepo"

    def __call__(self) -> list["Author"]:
        authors = self.repo.get_all()
        return authors


@attrs.frozen(kw_only=True, slots=True)
class CreateAuthorUseCase:
    """
    Use Case: Create an author.
    """

    repo: "AuthorRepo"

    def __call__(
        self,
        *,
        name: str,
    ) -> "Author":
        author = self.repo.create(name=name)
        return author


@attrs.frozen(kw_only=True, slots=True)
class FindAuthorsUseCase:
    """
    Use case: Find authors by attributes.
    """

    repo: "AuthorRepo"

    def __call__(
        self,
        *,
        name: str | None = None,
        id: UUID | None = None,  # noqa: A002
    ) -> list["Author"]:
        authors: list["Author"] | Generator[
            "Author", None, None
        ] = self.repo.get_all()

        if id is not None:
            authors = (author for author in authors if author.id == id)
        if name is not None:
            authors = (author for author in authors if author.name == name)

        return list(authors)


@attrs.frozen(kw_only=True, slots=True)
class UpdateAuthorUseCase:
    """
    Use Case: Update an author.
    """

    repo: "AuthorRepo"

    def __call__(
        self,
        *,
        id: "UUID",  # noqa: A002
        name: str,
    ) -> "Author":
        author = self.repo.update(id=id, name=name)
        return author


__all__ = (
    "CreateAuthorUseCase",
    "FindAuthorsUseCase",
    "GetAllAuthorsUseCase",
    "UpdateAuthorUseCase",
)

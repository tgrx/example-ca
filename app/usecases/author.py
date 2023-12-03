from typing import final

import attrs

from app.entities.errors import DuplicateAuthorNameError
from app.entities.errors import LostAuthorError
from app.entities.interfaces import AuthorRepo
from app.entities.models import ID
from app.entities.models import Author


@final
@attrs.frozen(kw_only=True, slots=True)
class CreateAuthorUseCase:
    """
    Use Case: Create an author.
    """

    repo: AuthorRepo

    def __call__(self, /, *, name: str) -> Author:
        self.ensure_name_is_unique(name)
        author = self.repo.create(name=name)

        return author

    def ensure_name_is_unique(self, name: str) -> None:
        name_is_taken = self.repo.get_by_name(name) is not None
        if name_is_taken:
            raise DuplicateAuthorNameError(name=name)


@final
@attrs.frozen(kw_only=True, slots=True)
class DeleteAuthorUseCase:
    """
    Use Case: Delete an author.
    """

    repo: AuthorRepo

    def __call__(self, author_id: ID, /) -> None:
        self.repo.delete(author_id)


@final
@attrs.frozen(kw_only=True, slots=True)
class FindAuthorsUseCase:
    """
    Use case: Find authors by attributes.
    """

    repo: AuthorRepo

    def __call__(
        self,
        /,
        *,
        author_id: ID | None = None,
        name: str | None = None,
    ) -> list[Author]:
        authors: list[Author] = []

        if all(arg is None for arg in (author_id, name)):
            authors.extend(self.repo.get_all())
        elif author_id is not None:
            author = self.repo.get_by_id(author_id)
            if author:
                authors.append(author)
        elif name is not None:
            author = self.repo.get_by_name(name)
            if author:
                authors.append(author)

        return authors


@final
@attrs.frozen(kw_only=True, slots=True)
class UpdateAuthorUseCase:
    """
    Use Case: Update an author.
    """

    repo: AuthorRepo

    def __call__(self, author_id: ID, /, *, name: str) -> Author:
        self.ensure_author_exists(author_id)
        self.ensure_name_is_unique(author_id, name)
        author = self.repo.update(author_id, name=name)

        return author

    def ensure_author_exists(self, author_id: ID) -> None:
        author = self.repo.get_by_id(author_id)
        if not author:
            raise LostAuthorError(author_id=author_id)

    def ensure_name_is_unique(self, author_id: ID, name: str) -> None:
        author = self.repo.get_by_id(author_id)
        assert author

        name_is_taken = self.repo.get_by_name(name) is not None
        if name != author.name and name_is_taken:
            raise DuplicateAuthorNameError(name=name)


__all__ = (
    "CreateAuthorUseCase",
    "DeleteAuthorUseCase",
    "FindAuthorsUseCase",
    "UpdateAuthorUseCase",
)

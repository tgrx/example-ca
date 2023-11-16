from typing import TYPE_CHECKING

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

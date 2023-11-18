"""
This module contains iterfaces.

Well, this is Python, so no interfaces.

Use protocols, "duck typing" polymorphism and structural subtyping, Luke.
"""

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from typing import Self
    from uuid import UUID

    from .models import Author
    from .models import Book


class AuthorRepo(Protocol):
    """
    This is how any Author repo MUST act.
    """

    def get_all(self: "Self") -> list["Author"]:
        """
        Use this to get all Author objects.
        """
        ...

    def create(
        self: "Self",
        *,
        name: str,
    ) -> "Author":
        """
        Use this to create a new Author object.
        """
        ...

    def delete(
        self: "Self",
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        """
        Use this to delete Author object using its id (pk).
        """
        ...

    def update(
        self: "Self",
        *,
        id: "UUID",  # noqa: A002
        name: str,
    ) -> "Author":
        """
        Use this to update Author with new data using its id (pk).
        """
        ...


class BookRepo(Protocol):
    """
    This is how any Book repo MUST act.
    """

    def create(
        self: "Self",
        *,
        author_ids: list["UUID"],
        title: str,
    ) -> "Book":
        """
        Use this to create a new Book object.
        """
        ...

    def delete(
        self: "Self",
        id: "UUID",  # noqa: A002,VNE003
    ) -> None:
        """
        Use this to delete Book object using its id (pk).
        """
        ...

    def get_all(self: "Self") -> list["Book"]:
        """
        Use this to get all Book objects.
        """
        ...

    def update(
        self: "Self",
        id: "UUID",  # noqa: A002,VNE003
        *,
        author_ids: list["UUID"] | None = None,
        title: str | None = None,
    ) -> "Book":
        """
        Use this to update Book with new data using its id (pk).
        """
        ...


__all__ = (
    "AuthorRepo",
    "BookRepo",
)

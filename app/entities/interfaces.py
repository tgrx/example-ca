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
        Use this to delee Author object using its id (pk).
        """
        ...


__all__ = ("AuthorRepo",)

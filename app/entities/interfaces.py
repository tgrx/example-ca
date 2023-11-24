"""
This module contains iterfaces.

Well, this is Python, so no interfaces.

Use protocols, "duck typing" polymorphism and structural subtyping, Luke.
"""

from typing import Collection
from typing import Protocol
from typing import Self

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


class AuthorRepo(Protocol):
    """
    This is how any Author repo MUST act.
    """

    def create(self: Self, /, *, name: str) -> Author:
        """
        Use this to create a new Author object.
        """
        ...

    def delete(self: Self, author_id: ID, /) -> None:
        """
        Use this to delete Author object using its ID.
        """
        ...

    def get_all(self: Self, /) -> list[Author]:
        """
        Use this to get all Author objects.
        """
        ...

    def get_by_id(self: Self, author_id: ID, /) -> Author | None:
        """
        Use this to get Author by ID.
        """
        ...

    def get_by_name(self: Self, name: str, /) -> Author | None:
        """
        Use this to get Author by name.
        """
        ...

    def update(self: Self, author_id: ID, /, *, name: str) -> Author:
        """
        Use this to update Author with new data using its ID.
        """
        ...


class BookRepo(Protocol):
    """
    This is how any Book repo MUST act.
    """

    def create(
        self: Self,
        /,
        *,
        author_ids: Collection[ID],
        title: str,
    ) -> Book:
        """
        Use this to create a new Book object.
        """
        ...

    def delete(self: Self, book_id: ID, /) -> None:
        """
        Use this to delete Book object using its ID.
        """
        ...

    def get_all(self: Self, /) -> list[Book]:
        """
        Use this to get all Book objects.
        """
        ...

    def get_by_id(self: Self, book_id: ID, /) -> Book | None:
        """
        Use this to get Book by ID.
        """
        ...

    def get_by_title(self: Self, title: str, /) -> Book | None:
        """
        Use this to get Book by title.
        """
        ...

    def update(
        self: Self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        """
        Use this to update Book with new data using its id (pk).
        """
        ...


__all__ = (
    "AuthorRepo",
    "BookRepo",
)

from typing import TYPE_CHECKING
from typing import Generator
from uuid import UUID

import attrs

if TYPE_CHECKING:
    from app.entities.interfaces import BookRepo
    from app.entities.models import Book


@attrs.frozen(kw_only=True, slots=True)
class GetAllBooksUseCase:
    """
    Use case: Get all books.
    """

    repo: "BookRepo"

    def __call__(self) -> list["Book"]:
        books = self.repo.get_all()
        return books


@attrs.frozen(kw_only=True, slots=True)
class CreateBookUseCase:
    """
    Use Case: Create a book.
    """

    repo: "BookRepo"

    def __call__(
        self,
        *,
        author_ids: list["UUID"],
        title: str,
    ) -> "Book":
        book = self.repo.create(
            author_ids=author_ids,
            title=title,
        )
        return book


@attrs.frozen(kw_only=True, slots=True)
class FindBooksUseCase:
    """
    Use case: Find books by attributes.
    """

    repo: "BookRepo"

    def __call__(
        self,
        *,
        id: UUID | None = None,  # noqa:A002
        title: str | None = None,
    ) -> list["Book"]:
        books: list["Book"] | Generator["Book", None, None]
        books = self.repo.get_all()

        if id is not None:
            books = (book for book in books if book.id == id)

        if title is not None:
            books = (book for book in books if book.title == title)

        return list(books)


@attrs.frozen(kw_only=True, slots=True)
class UpdateBookUseCase:
    """
    Use Case: Update a book.
    """

    repo: "BookRepo"

    def __call__(
        self,
        id: "UUID",  # noqa: A002,VNE003
        *,
        author_ids: list["UUID"] | None = None,
        title: str | None = None,
    ) -> "Book":
        book = self.repo.update(
            id,
            author_ids=author_ids,
            title=title,
        )
        return book


__all__ = (
    "CreateBookUseCase",
    "FindBooksUseCase",
    "GetAllBooksUseCase",
    "UpdateBookUseCase",
)

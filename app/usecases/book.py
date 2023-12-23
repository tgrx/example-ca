from typing import Collection
from typing import final

import attrs

from app.entities.interfaces import BookRepo
from app.entities.models import ID
from app.entities.models import Book


@final
@attrs.frozen(kw_only=True, slots=True)
class CreateBookUseCase:
    """
    Use Case: Create a book.
    """

    repo: BookRepo

    def __call__(self, /, *, title: str) -> Book:
        book = self.repo.create(title=title)
        return book


@final
@attrs.frozen(kw_only=True, slots=True)
class DeleteBookUseCase:
    """
    Use Case: Delete a book.
    """

    repo: BookRepo

    def __call__(self, book_id: ID, /) -> None:
        self.repo.delete(book_id)


@final
@attrs.frozen(kw_only=True, slots=True)
class FindBooksUseCase:
    """
    Use case: Find books by attributes.
    """

    repo: BookRepo

    def __call__(
        self,
        /,
        *,
        book_id: ID | None = None,
        title: str | None = None,
    ) -> list[Book]:
        books: list[Book] = []

        if all(arg is None for arg in (book_id, title)):
            books.extend(self.repo.get_all())
        elif book_id is not None:
            book = self.repo.get_by_id(book_id)
            if book:
                books.append(book)
        elif title is not None:
            book = self.repo.get_by_title(title)
            if book:
                books.append(book)

        return books


@final
@attrs.frozen(kw_only=True, slots=True)
class UpdateBookUseCase:
    """
    Use Case: Update a book.
    """

    repo: BookRepo

    def __call__(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        book = self.repo.update(book_id, author_ids=author_ids, title=title)
        return book


__all__ = (
    "CreateBookUseCase",
    "DeleteBookUseCase",
    "FindBooksUseCase",
    "UpdateBookUseCase",
)

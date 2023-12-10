from typing import Collection
from typing import final

import attrs

from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostBookError
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
        self.ensure_title_is_unique(title)

        book = self.repo.create(title=title)

        return book

    def ensure_title_is_unique(self, title: str) -> None:
        title_is_taken = self.repo.get_by_title(title) is not None
        if title_is_taken:
            raise DuplicateBookTitleError(title=title)


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
        self.ensure_book_exists(book_id)
        self.ensure_title_is_unique(book_id, title)

        book = self.repo.update(book_id, author_ids=author_ids, title=title)

        return book

    def ensure_book_exists(self, book_id: ID, /) -> None:
        book = self.repo.get_by_id(book_id)
        if book is None:
            raise LostBookError(book_id=book_id)

    def ensure_title_is_unique(
        self,
        book_id: ID,
        title: str | None,
        /,
    ) -> None:
        if title is None:
            return

        book = self.repo.get_by_id(book_id)
        if book is None:
            raise LostBookError(book_id=book_id)

        title_is_taken = self.repo.get_by_title(title) is not None
        if title != book.title and title_is_taken:
            raise DuplicateBookTitleError(title=title)


__all__ = (
    "CreateBookUseCase",
    "DeleteBookUseCase",
    "FindBooksUseCase",
    "UpdateBookUseCase",
)

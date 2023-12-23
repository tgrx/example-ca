from typing import Collection
from typing import Mapping
from typing import MutableMapping
from typing import final
from uuid import uuid4

import attrs

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    index_authors: Mapping[ID, Author]
    index_books_authors: MutableMapping[ID, set[ID]]
    index_books: MutableMapping[ID, Book]

    def create(self, /, *, title: str) -> Book:
        self._raise_on_duplicate_title(title)

        book_id = uuid4()
        book = Book(author_ids=[], book_id=book_id, title=title)
        self.index_books[book_id] = book

        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        return book

    def delete(self, book_id: ID, /) -> None:
        book = self.get_by_id(book_id)
        if book is None:
            return

        self._raise_on_degenerate_authors(book.author_ids)
        self.index_books.pop(book_id, ...)
        self.index_books_authors.pop(book_id, ...)

    def get_all(self, /) -> list[Book]:
        raw_books = map(self.get_by_id, self.index_books)
        existing_books = filter(lambda i: i is not None, raw_books)
        sorted_books = sorted(existing_books, key=lambda i: i.title)
        return sorted_books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        book = self.index_books.get(book_id)
        if book is None:
            return None

        author_ids = set(self.index_books_authors.get(book_id, []))
        author_ids = self._clean_author_ids(author_ids)
        book = book.model_copy(update={"author_ids": author_ids})
        self.index_books[book_id] = book
        return book

    def get_by_title(self, title: str, /) -> Book | None:
        for book in self.index_books.values():
            if book.title == title:
                break
        else:
            book = None

        if book is None:
            return None

        book = self.get_by_id(book.book_id)
        return book

    def update(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        if author_ids is None and title is None:
            return book

        new_author_ids = self._clean_author_ids(author_ids)

        if book.author_ids == new_author_ids and book.title == title:
            return book

        update = {}
        if author_ids is not None:
            current_author_ids = set(book.author_ids)
            discarded_author_ids = current_author_ids - set(new_author_ids)
            self._raise_on_degenerate_authors(discarded_author_ids)
            update["author_ids"] = new_author_ids
        if title is not None:
            self._raise_on_duplicate_title(title)
            update["title"] = title

        book = book.model_copy(update=update)
        self.index_books[book_id] = book
        self._update_references(book)
        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_id=book_id, title=title)

        return book

    def _clean_author_ids(
        self,
        author_ids: Collection[ID],
        /,
    ) -> list[ID]:
        author_ids = set(author_ids or [])
        if not author_ids:
            return []

        existing_author_ids = set(self.index_authors.keys())
        lost_author_ids = author_ids - existing_author_ids
        if lost_author_ids:
            raise LostAuthorsError(author_ids=lost_author_ids)

        author_ids &= existing_author_ids
        sorted_author_ids = sorted(
            author_ids,
            key=lambda i: self.index_authors[i].name,
        )

        return sorted_author_ids

    def _raise_on_degenerate_authors(
        self,
        author_ids: Collection[ID],
        /,
    ) -> None:
        degenerate = {}
        for author_id in author_ids:
            refs = (
                author_id in refs for refs in self.index_books_authors.values()
            )
            number_of_refs = sum(refs)
            if number_of_refs > 1:
                continue
            author = self.index_authors[author_id]
            degenerate[author.name] = author.author_id

        if degenerate:
            raise DegenerateAuthorsError(authors=degenerate)

    def _raise_on_duplicate_title(self, title: str, /) -> None:
        for book in self.index_books.values():
            if book.title == title:
                raise DuplicateBookTitleError(title=title)

    def _update_references(self, book: Book, /) -> None:
        author_ids = self._clean_author_ids(book.author_ids)
        self.index_books_authors[book.book_id] = author_ids


__all__ = ("BookRepo",)

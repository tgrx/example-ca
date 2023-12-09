from typing import Collection
from typing import Mapping
from typing import MutableMapping
from typing import final
from uuid import uuid4

import attrs

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import LostAuthorError
from app.entities.errors import LostBookError
from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    index_authors: Mapping[ID, Author]
    index_ba: dict[ID, set[ID]]
    index_books: MutableMapping[ID, Book]

    def create(self, /, *, title: str) -> Book:
        book_id = uuid4()
        book = Book(authors=(), book_id=book_id, title=title)
        self.index_books[book_id] = book
        book = self.get_by_id(book_id)
        if book is None:
            raise LostBookError(book_id=book_id, title=title)
        return book

    def delete(self, book_id: ID, /) -> None:
        book = self.get_by_id(book_id)
        if book is None:
            return
        author_ids = {author.author_id for author in book.authors}
        self._raise_on_degenerate_authors(author_ids)
        self.index_books.pop(book_id, ...)
        self.index_ba.pop(book_id, ...)

    def get_all(self, /) -> list[Book]:
        raw_books = (self.get_by_id(book_id) for book_id in self.index_books)
        existing_books = (book for book in raw_books if book is not None)
        sorted_books = sorted(
            existing_books,
            key=lambda book: book.title,
        )
        return sorted_books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        book = self.index_books.get(book_id)
        if book is None:
            return None

        author_ids = set(self.index_ba.get(book_id, ()))
        authors = self._get_authors_by_ids(author_ids)
        book = book.model_copy(update={"authors": authors})
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
            raise LostBookError(book_id=book_id)

        if author_ids is None and title is None:
            return book

        authors = self._get_authors_by_ids(author_ids)

        if book.authors == authors and book.title == title:
            return book

        update = {}
        if author_ids is not None:
            current_author_ids = {author.author_id for author in book.authors}
            new_author_ids = {author.author_id for author in authors}
            discarded_author_ids = current_author_ids - new_author_ids
            self._raise_on_degenerate_authors(discarded_author_ids)
            update["authors"] = authors
        if title is not None:
            update["title"] = title

        book = book.model_copy(update=update)
        self.index_books[book_id] = book
        self._update_references(book)
        book = self.get_by_id(book_id)
        if book is None:
            raise LostBookError(book_id=book_id, title=title)
        return book

    def _get_authors_by_ids(
        self,
        author_ids: Collection[ID],
        /,
    ) -> tuple[Author, ...]:
        author_ids = set(author_ids or ())
        if not author_ids:
            return ()

        try:
            unique_authors = {
                self.index_authors[author_id] for author_id in author_ids
            }
            authors = sorted(
                unique_authors,
                key=lambda author: author.name,
            )
            authors = tuple(authors)
            return authors
        except KeyError as exc:
            missing_author_id = exc.args[0]
            raise LostAuthorError(author_id=missing_author_id) from exc

    def _raise_on_degenerate_authors(
        self,
        author_ids: Collection[ID],
        /,
    ) -> None:
        degenerate = {}
        for author_id in author_ids:
            number_of_refs = sum(
                author_id in refs for refs in self.index_ba.values()
            )
            if number_of_refs > 1:
                continue
            author = self.index_authors[author_id]
            degenerate[author.name] = author.author_id

        if degenerate:
            raise DegenerateAuthorsError(authors=degenerate)

    def _update_references(self, book: Book, /) -> None:
        author_ids = {author.author_id for author in book.authors}
        self.index_ba[book.book_id] = author_ids


__all__ = ("BookRepo",)

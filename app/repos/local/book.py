from typing import Iterable
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
    index_books: MutableMapping[ID, Book]

    def create(self, /, *, title: str) -> Book:
        book_id = uuid4()
        book = Book(authors=[], book_id=book_id, title=title)
        self.index_books[book_id] = book
        self._update_references()
        return book

    def delete(self, book_id: ID, /) -> None:
        book = self.index_books.get(book_id)
        if book is None:
            return
        author_ids = {a.author_id for a in book.authors}
        self._raise_on_degenerate_authors(author_ids, book_id)
        del self.index_books[book_id]
        self._update_references()

    def get_all(self, /) -> list[Book]:
        books = list(self.index_books.values())
        return books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        book = self.index_books.get(book_id)
        return book

    def get_by_title(self, title: str, /) -> Book | None:
        for book in self.index_books.values():
            if book.title == title:
                break
        else:
            book = None

        return book

    def update(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Iterable[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        book = self.index_books.get(book_id)
        if book is None:
            raise LostBookError(book_id=book_id)

        if author_ids is None and title is None:
            return book

        authors = self._get_authors_by_ids(author_ids)

        if book.authors == authors and book.title == title:
            return book

        update = {}

        if author_ids is not None:
            excluded_author_ids = {
                a.author_id
                for a in book.authors
                if a.author_id not in author_ids
            }
            self._raise_on_degenerate_authors(excluded_author_ids, book_id)
            authors = self._get_authors_by_ids(author_ids)
            update["authors"] = authors

        if title is not None:
            update["title"] = title

        book = book.model_copy(update=update)
        self.index_books[book_id] = book
        self._update_references()

        return book

    def _get_authors_by_ids(
        self,
        author_ids: Iterable[ID],
        /,
    ) -> list[Author]:
        author_ids = set(author_ids or [])
        if not author_ids:
            return []

        try:
            authors = sorted(
                {self.index_authors[author_id] for author_id in author_ids},
                key=lambda author: author.name,
            )
            return authors
        except KeyError as exc:
            missing_author_id = exc.args[0]
            raise LostAuthorError(author_id=missing_author_id) from exc

    def _raise_on_degenerate_authors(
        self,
        author_ids: Iterable[ID],
        book_id: ID,
        /,
    ) -> None:
        degenerate = {}
        author_ids = set(author_ids or []) & self.index_authors
        for author_id in author_ids:
            author = self.index_authors.get(author_id)
            book_ids = {
                b.book_id for b in author.books if b.book_id != book_id
            }
            if book_ids:
                continue

            degenerate[author.name] = author.author_id

        if degenerate:
            raise DegenerateAuthorsError(authors=degenerate)

    def _update_references(self, /) -> None:
        for book in self.index_books.values():
            for author in book.authors:
                author.books.append(book)

        for author in self.index_authors.values():
            author.books = sorted(
                {
                    self.index_books[book_id]
                    for book_id in {b.book_id for b in author.books}
                },
                key=lambda b: b.title,
            )


__all__ = ("BookRepo",)

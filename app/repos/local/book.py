from typing import Collection
from typing import final
from uuid import uuid4

import attrs

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    index_authors: dict[ID, Author]
    index_books: dict[ID, Book]

    def create(self, /, *, author_ids: Collection[ID], title: str) -> Book:
        authors = [self.index_authors[author_id] for author_id in author_ids]
        authors.sort(key=lambda _author: (_author.name, _author.author_id))
        book_id = uuid4()
        book = Book(authors=authors, book_id=book_id, title=title)
        self.index_books[book_id] = book

        return book

    def delete(self, book_id: ID, /) -> None:
        self.index_books.pop(book_id, ...)

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
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Author:
        book = self.index_books[book_id]

        if all(arg is None for arg in (author_ids, title)):
            return book

        if author_ids is not None:
            authors = [
                self.index_authors[author_id] for author_id in author_ids
            ]
            authors.sort(key=lambda _a: (_a.name, _a.author_id))
        else:
            authors = book.authors

        if title is not None:
            new_title = title
        else:
            new_title = book.title

        book = book.model_copy(
            update={
                "authors": authors,
                "title": new_title,
            },
        )
        self.index_books[book_id] = book

        return book


__all__ = ("BookRepo",)

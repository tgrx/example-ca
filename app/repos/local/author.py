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
class AuthorRepo:
    index_authors: MutableMapping[ID, Author]
    index_books: Mapping[ID, Book]

    def create(self, /, *, book_ids: Iterable[ID], name: str) -> Author:
        author_id = uuid4()
        books = self._get_books_by_ids(book_ids)
        author = Author(author_id=author_id, books=books, name=name)
        self._raise_on_degenerate_author(author, indexed=False)
        self.index_authors[author_id] = author
        self._update_references()
        return author

    def delete(self, author_id: ID, /) -> None:
        self.index_authors.pop(author_id, ...)
        self._update_references()

    def get_all(self, /) -> list[Author]:
        authors = list(self.index_authors.values())
        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        for author in self.index_authors.values():
            if author.name == name:
                break
        else:
            author = None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author = self.index_authors.get(author_id)
        return author

    def update(
        self,
        author_id: ID,
        /,
        *,
        book_ids: Iterable[ID] | None = None,
        name: str | None,
    ) -> Author:
        author = self.index_authors.get(author_id)
        if author is None:
            raise LostAuthorError(author_id=author_id)

        if name is None and book_ids is None:
            return author

        books = self._get_books_by_ids(book_ids)

        if author.name == name and author.books == books:
            return author

        update = {}

        if name is not None:
            update["name"] = name

        if book_ids is not None:
            books = self._get_books_by_ids(book_ids)
            update["books"] = books

        author = author.model_copy(update=update)
        self._raise_on_degenerate_author(author)
        self.index_authors[author.author_id] = author
        self._update_references()
        return author

    def _get_books_by_ids(
        self,
        book_ids: Iterable[ID] | None,
        /,
    ) -> list[Book]:
        book_ids = set(book_ids or [])
        if not book_ids:
            return []

        try:
            books = sorted(
                {self.index_books[book_id] for book_id in book_ids},
                key=lambda book: book.title,
            )
            return books
        except KeyError as exc:
            missing_book_id = exc.args[0]
            raise LostBookError(book_id=missing_book_id) from exc

    def _raise_on_degenerate_author(
        self,
        author: Author,
        /,
        *,
        indexed: bool = True,
    ) -> None:
        if not author.books:
            raise DegenerateAuthorsError(
                authors={
                    author.name: author.author_id if indexed else None,
                },
            )

    def _update_references(self, /) -> None:
        for author in self.index_authors.values():
            for book in author.books:
                book.authors.append(author)

        for book in self.index_books.values():
            book.authors = sorted(
                {
                    self.index_authors[author_id]
                    for author_id in {a.author_id for a in book.authors}
                },
                key=lambda a: a.name,
            )


__all__ = ("AuthorRepo",)

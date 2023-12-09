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
class AuthorRepo:
    index_authors: MutableMapping[ID, Author]
    index_ba: dict[ID, set[ID]]
    index_books: Mapping[ID, Book]

    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        author_id = uuid4()
        books = self._get_books_by_ids(book_ids)
        author = Author(author_id=author_id, books=books, name=name)
        self._raise_on_degenerate_author(author, indexed=False)
        self.index_authors[author_id] = author
        self._update_references(author)
        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorError(author_id=author_id, name=name)
        return author

    def delete(self, author_id: ID, /) -> None:
        author = self.index_authors.pop(author_id, None)
        self._update_references(author)

    def get_all(self, /) -> list[Author]:
        raw_authors = (
            self.get_by_id(author_id) for author_id in self.index_authors
        )
        existing_authors = (
            author for author in raw_authors if author is not None
        )
        sorted_authors = sorted(
            existing_authors,
            key=lambda author: author.name,
        )
        return sorted_authors

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author = self.index_authors.get(author_id)
        if author is None:
            return None

        book_ids = {
            book_id
            for book_id, refs in self.index_ba.items()
            if author_id in refs
        }
        books = self._get_books_by_ids(book_ids)
        author = author.model_copy(update={"books": books})
        self.index_authors[author_id] = author
        return author

    def get_by_name(self, name: str, /) -> Author | None:
        for author in self.index_authors.values():
            if author.name == name:
                break
        else:
            author = None

        if author is None:
            return None

        author = self.get_by_id(author.author_id)
        return author

    def update(
        self,
        author_id: ID,
        /,
        *,
        book_ids: Collection[ID] | None = None,
        name: str | None,
    ) -> Author:
        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorError(author_id=author_id)

        if book_ids is None and name is None:
            return author

        books = self._get_books_by_ids(book_ids)

        if author.books == books and author.name == name:
            return author

        update = {}
        if book_ids is not None:
            update["books"] = books
        if name is not None:
            update["name"] = name

        author = author.model_copy(update=update)
        self._raise_on_degenerate_author(author)
        self.index_authors[author.author_id] = author
        self._update_references(author)
        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorError(author_id=author_id, name=name)
        return author

    def _get_books_by_ids(
        self,
        book_ids: Collection[ID] | None,
        /,
    ) -> tuple[Book, ...]:
        book_ids = set(book_ids or ())
        if not book_ids:
            return ()

        try:
            unique_books = {self.index_books[book_id] for book_id in book_ids}
            books = sorted(
                unique_books,
                key=lambda book: book.title,
            )
            books = tuple(books)
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
                    author.name: (author.author_id if indexed else None),
                },
            )

    def _update_references(self, author: Author | None, /) -> None:
        book_ids_to_discard = self.index_ba.keys() - self.index_books.keys()
        for book_id in book_ids_to_discard:
            self.index_ba.pop(book_id, ...)

        for refs in self.index_ba.values():
            refs &= self.index_authors.keys()

        if author is None:
            return

        book_ids = {b.book_id for b in author.books}
        books = self._get_books_by_ids(book_ids)
        if not books:
            raise DegenerateAuthorsError(
                authors={author.name: author.author_id}
            )

        book_ids = {b.book_id for b in books}

        for refs in self.index_ba.values():
            refs.discard(author.author_id)

        for book_id in book_ids:
            self.index_ba.setdefault(book_id, set()).add(author.author_id)


__all__ = ("AuthorRepo",)

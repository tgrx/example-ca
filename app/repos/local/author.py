from typing import Collection
from typing import Mapping
from typing import MutableMapping
from typing import final
from uuid import uuid4

import attrs

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    index_authors: MutableMapping[ID, Author]
    index_books_authors: MutableMapping[ID, set[ID]]
    index_books: Mapping[ID, Book]

    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        author_id = uuid4()
        new_book_ids = self._clean_book_ids(book_ids)

        author = Author(author_id=author_id, book_ids=new_book_ids, name=name)
        self._raise_on_degenerate_author(author, indexed=False)
        self.index_authors[author_id] = author
        self._update_references(author)

        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorsError(author_ids=[author_id])

        return author

    def delete(self, author_id: ID, /) -> None:
        author = self.index_authors.pop(author_id, None)
        self._update_references(author)

    def get_all(self, /) -> list[Author]:
        raw_authors = map(self.get_by_id, self.index_authors)
        existing_authors = filter(lambda item: item is not None, raw_authors)
        sorted_authors = sorted(existing_authors, key=lambda item: item.name)
        return sorted_authors

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author = self.index_authors.get(author_id)
        if author is None:
            return None

        book_ids = {
            book_id
            for book_id, refs in self.index_books_authors.items()
            if author_id in refs
        }
        book_ids = self._clean_book_ids(book_ids)

        author = author.model_copy(update={"book_ids": book_ids})
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
            raise LostAuthorsError(author_ids=[author_id])

        if book_ids is None and name is None:
            return author

        cleaned_book_ids = self._clean_book_ids(book_ids or [])
        if author.book_ids == cleaned_book_ids and author.name == name:
            return author

        update = {}
        if book_ids is not None:
            update["book_ids"] = cleaned_book_ids
        if name is not None:
            update["name"] = name

        author = author.model_copy(update=update)
        self._raise_on_degenerate_author(author)
        self.index_authors[author.author_id] = author
        self._update_references(author)
        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorsError(author_ids=[author_id])

        return author

    def _clean_book_ids(self, book_ids: Collection[ID], /) -> list[ID]:
        book_ids = set(book_ids or [])
        if not book_ids:
            return []

        existing_book_ids = set(self.index_books.keys())
        lost_book_ids = book_ids - existing_book_ids
        if lost_book_ids:
            raise LostBooksError(book_ids=lost_book_ids)

        book_ids &= existing_book_ids
        sorted_book_ids = sorted(
            book_ids,
            key=lambda book_id: self.index_books[book_id].title,
        )

        return sorted_book_ids

    def _raise_on_degenerate_author(
        self,
        author: Author,
        /,
        *,
        indexed: bool = True,
    ) -> None:
        if not author.book_ids:
            author_id = author.author_id if indexed else None
            raise DegenerateAuthorsError(
                authors={author.name: author_id},
            )

    def _update_references(self, author: Author | None, /) -> None:
        book_ids_to_discard = (
            self.index_books_authors.keys() - self.index_books.keys()
        )
        for book_id in book_ids_to_discard:
            self.index_books_authors.pop(book_id, ...)

        for refs in self.index_books_authors.values():
            refs &= self.index_authors.keys()

        if author is None:
            return

        book_ids = set(author.book_ids)
        book_ids = self._clean_book_ids(book_ids)
        if not book_ids:
            raise DegenerateAuthorsError(
                authors={author.name: author.author_id}
            )

        for refs in self.index_books_authors.values():
            refs.discard(author.author_id)

        for book_id in book_ids:
            refs = self.index_books_authors.setdefault(book_id, set())
            refs.add(author.author_id)


__all__ = ("AuthorRepo",)

from typing import Collection
from typing import final
from uuid import uuid4

import attrs
from django.db import transaction

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import LostAuthorsError
from app.entities.models import ID
from app.entities.models import Book
from app_api_v1.models import Author as OrmAuthor
from app_api_v3.models import Book as OrmBook


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    def create(self, /, *, title: str) -> Book:
        book_id = uuid4()

        orm_book = OrmBook(pk=book_id, title=title)
        orm_book.save()

        book = Book.model_validate(orm_book)

        return book

    def delete(self, book_id: ID, /) -> None:
        try:
            record = OrmBook.objects.get(pk=book_id)
            record.delete()

        except OrmBook.DoesNotExist:
            pass

    def get_all(self, /) -> list[Book]:
        orm_books = OrmBook.objects.prefetch_related("authors").all()
        books = [Book.model_validate(i) for i in orm_books]

        return books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        book: Book | None

        try:
            orm_books = OrmBook.objects.prefetch_related("authors")
            orm_book = orm_books.get(pk=book_id)
            book = Book.model_validate(orm_book)
        except OrmBook.DoesNotExist:
            book = None

        return book

    def get_by_title(self, title: str, /) -> Book | None:
        book: Book | None

        try:
            orm_books = OrmBook.objects.prefetch_related("authors")
            orm_book = orm_books.get(title=title)
            book = Book.model_validate(orm_book)

        except OrmBook.DoesNotExist:
            book = None

        return book

    def update(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        orm_book = OrmBook.objects.get(pk=book_id)

        if author_ids is not None:
            new_author_ids = self._clean_author_ids(author_ids)
            self._raise_on_degenerate_authors(new_author_ids, orm_book)

        with transaction.atomic():
            if title is not None:
                orm_book.title = title
                orm_book.save()

            if author_ids is not None:
                orm_book.authors.clear()
                orm_book.authors.add(*new_author_ids)  # type: ignore

        book = Book.model_validate(orm_book)

        return book

    def _clean_author_ids(
        self,
        author_ids: Collection[ID],
        /,
    ) -> Collection[ID]:
        raw_author_ids = sorted(set(author_ids))
        authors = (
            OrmAuthor.objects.filter(pk__in=raw_author_ids)
            .order_by("name")
            .all()
        )
        clean_author_ids = [i.author_id for i in authors]

        lost_author_ids = [
            i for i in raw_author_ids if i not in clean_author_ids
        ]
        if lost_author_ids:
            raise LostAuthorsError(author_ids=lost_author_ids)

        return clean_author_ids

    def _raise_on_degenerate_authors(
        self,
        new_author_ids: Collection[ID],
        orm_book: OrmBook,
        /,
    ) -> None:
        discard_author_ids = [
            i for i in orm_book.author_ids if i not in new_author_ids
        ]
        if not discard_author_ids:
            return

        discard_authors = (
            OrmAuthor.objects.filter(pk__in=discard_author_ids)
            .prefetch_related("books")
            .all()
        )

        degenerate_authors = [
            i for i in discard_authors if i.book_ids == [orm_book.book_id]
        ]
        if degenerate_authors:
            degenerate_map = {i.name: i.pk for i in degenerate_authors}
            raise DegenerateAuthorsError(authors=degenerate_map)


__all__ = ("BookRepo",)

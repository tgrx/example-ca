from typing import Collection
from typing import final
from uuid import uuid4

import attrs

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from app_api_v3.models import Book as OrmBook


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    def create(self, /, *, title: str) -> Book:
        book_id = uuid4()
        orm_book = OrmBook(pk=book_id, title=title)
        orm_book.save()

        authors: tuple[Author, ...] = ()
        book = Book(
            authors=authors,
            book_id=orm_book.pk,
            title=orm_book.title,
        )

        return book

    def delete(self, book_id: ID, /) -> None:
        try:
            record = OrmBook.objects.get(pk=book_id)
            record.delete()

        except OrmBook.DoesNotExist:
            pass

    def get_all(self, /) -> list[Book]:
        orm_books = OrmBook.objects.prefetch_related("authors").all()

        books = [
            Book(
                authors=tuple(
                    Author.model_validate(orm_author)
                    for orm_author in orm_book.authors.order_by(
                        "name",
                        "pk",
                    ).all()
                ),
                book_id=orm_book.pk,
                title=orm_book.title,
            )
            for orm_book in orm_books
        ]

        return books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        book: Book | None

        try:
            orm_books = OrmBook.objects.prefetch_related("authors")
            orm_book = orm_books.get(pk=book_id)

            authors = tuple(
                Author.model_validate(orm_author)
                for orm_author in orm_book.authors.order_by("name", "pk").all()
            )

            book = Book(
                authors=authors,
                book_id=orm_book.pk,
                title=orm_book.title,
            )

        except OrmBook.DoesNotExist:
            book = None

        return book

    def get_by_title(self, title: str, /) -> Book | None:
        book: Book | None

        try:
            orm_books = OrmBook.objects.prefetch_related("authors")
            orm_book = orm_books.get(title=title)

            authors = tuple(
                Author.model_validate(orm_author)
                for orm_author in orm_book.authors.order_by("name", "pk").all()
            )

            book = Book(
                authors=authors,
                book_id=orm_book.pk,
                title=orm_book.title,
            )

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

        if title is not None:
            orm_book.title = title

        if author_ids is not None:
            orm_book.authors.clear()
            if author_ids:
                author_ids = sorted(set(author_ids))
                orm_book.authors.add(*author_ids)  # type: ignore

        orm_book.save()

        authors = tuple(
            Author.model_validate(orm_author)
            for orm_author in orm_book.authors.order_by("name", "pk").all()
        )

        book = Book(
            authors=authors,
            book_id=orm_book.pk,
            title=orm_book.title,
        )

        return book


__all__ = ("BookRepo",)

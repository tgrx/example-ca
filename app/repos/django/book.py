from typing import TYPE_CHECKING
from typing import Type
from uuid import uuid4

import attrs

from app.entities.models import Author
from app.entities.models import Book

if TYPE_CHECKING:
    from uuid import UUID

    from app_api_v3.models import Book as BookDjangoModel


@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    model: Type["BookDjangoModel"]  # to untangle repo from non-django code

    def create(
        self,
        *,
        author_ids: list["UUID"],
        title: str,
    ) -> "Book":
        # todo: transaction
        record_book = self.model(
            id=uuid4(),
            title=title,
        )
        # todo: what if obj already exist, or another integrity error?
        # todo: what if db is down?
        record_book.save()

        # todo: check that no authors => error
        record_book.authors.add(*author_ids)  # type: ignore  # pk is uuid

        book = Book(
            authors=[
                Author.model_validate(record_author)
                for record_author in record_book.authors.order_by(
                    "name", "pk"
                ).all()
            ],
            id=record_book.id,
            title=record_book.title,
        )

        return book

    def delete(
        self,
        id: "UUID",  # noqa: A002,VNE003
    ) -> None:
        try:
            record = self.model.objects.get(pk=id)
            # todo: what if integrity error?
            # todo: what if db is down?
            record.delete()
        except self.model.DoesNotExist:
            pass

    def get_all(self) -> list["Book"]:
        records = self.model.objects.all()
        books = [
            Book(
                id=record_book.id,
                title=record_book.title,
                authors=[
                    Author.model_validate(record_author)
                    for record_author in record_book.authors.order_by(
                        "name", "pk"
                    ).all()
                ],
            )
            for record_book in records
        ]
        return books

    def update(
        self,
        id: "UUID",  # noqa: A002,VNE003
        *,
        author_ids: list["UUID"] | None = None,
        title: str | None = None,
    ) -> "Book":
        # todo: at least one of title, author_ids
        record_book = self.model.objects.get(pk=id)

        # todo: transaction
        if title is not None:
            record_book.title = title

        if author_ids is not None:
            record_book.authors.clear()
            # todo: what if there are no authors?
            record_book.authors.add(*author_ids)  # type: ignore  # pk is uuid

        record_book.save()
        book = Book(
            authors=[
                Author.model_validate(record_author)
                for record_author in record_book.authors.order_by(
                    "name", "pk"
                ).all()
            ],
            id=record_book.id,
            title=record_book.title,
        )
        return book


__all__ = ("BookRepo",)

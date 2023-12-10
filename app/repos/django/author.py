from typing import Collection
from typing import final
from uuid import uuid4

import attrs

from app.entities.models import ID
from app.entities.models import Author
from app_api_v1.models import Author as OrmAuthor


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        # todo: raise on degenerate: no books
        # todo: transaction
        author_id = uuid4()
        orm_author = OrmAuthor(name=name, pk=author_id)
        orm_author.save()

        book_ids = sorted(set(book_ids))
        # todo: check for lost book ids
        orm_author.books.add(*book_ids)  # type: ignore

        book_ids = self._get_book_ids(orm_author)
        author = Author(
            author_id=orm_author.pk,
            book_ids=book_ids,
            name=orm_author.name,
        )

        return author

    def delete(self, author_id: ID, /) -> None:
        try:
            record = OrmAuthor.objects.get(pk=author_id)
            record.delete()
        except OrmAuthor.DoesNotExist:
            pass

    def get_all(self, /) -> list[Author]:
        records = OrmAuthor.objects.all()
        # todo: author explicit creation
        authors = [Author.model_validate(record) for record in records]
        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        author: Author | None

        try:
            record = OrmAuthor.objects.get(name=name)
            # todo: author explicit creation
            author = Author.model_validate(record)
        except OrmAuthor.DoesNotExist:
            author = None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author: Author | None

        try:
            record = OrmAuthor.objects.get(pk=author_id)
            # todo: author explicit creation
            author = Author.model_validate(record)
        except OrmAuthor.DoesNotExist:
            author = None

        return author

    def update(
        self,
        author_id: ID,
        /,
        *,
        book_ids: Collection[ID] | None = None,
        name: str | None = None,
    ) -> Author:
        # todo: books
        record = OrmAuthor.objects.get(pk=author_id)
        if name is not None:
            record.name = name
        # todo: transaction
        record.save()

        # todo: author explicit creation
        author = Author.model_validate(record)
        return author

    def _get_book_ids(self, orm_author: OrmAuthor, /) -> list[ID]:
        book_ids = [
            i.book_id for i in orm_author.books.order_by("title").all()
        ]
        return book_ids


__all__ = ("AuthorRepo",)

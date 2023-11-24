from typing import final
from uuid import uuid4

import attrs

from app.entities.models import ID
from app.entities.models import Author
from app_api_v1.models import Author as OrmAuthor


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    def create(self, /, *, name: str) -> Author:
        author_id = uuid4()
        record = OrmAuthor(name=name, pk=author_id)
        record.save()
        author = Author.model_validate(record)

        return author

    def delete(self, author_id: ID, /) -> None:
        try:
            record = OrmAuthor.objects.get(pk=author_id)
            record.delete()
        except OrmAuthor.DoesNotExist:
            pass

    def get_all(self, /) -> list[Author]:
        records = OrmAuthor.objects.all()
        authors = [Author.model_validate(record) for record in records]
        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        author: Author | None

        try:
            record = OrmAuthor.objects.get(name=name)
            author = Author.model_validate(record)
        except OrmAuthor.DoesNotExist:
            author = None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author: Author | None

        try:
            record = OrmAuthor.objects.get(pk=author_id)
            author = Author.model_validate(record)
        except OrmAuthor.DoesNotExist:
            author = None

        return author

    def update(self, author_id: ID, /, *, name: str) -> Author:
        record = OrmAuthor.objects.get(pk=author_id)
        record.name = name
        record.save()

        author = Author.model_validate(record)
        return author


__all__ = ("AuthorRepo",)

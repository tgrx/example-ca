from typing import Collection
from typing import final
from uuid import uuid4

import attrs
from django.db import transaction

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateAuthorNameError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
from app.entities.models import ID
from app.entities.models import Author
from app_api_v1.models import Author as OrmAuthor
from app_api_v3.models import Book as OrmBook


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        self._raise_on_duplicate_name(name)
        clean_book_ids = self._clean_book_ids(book_ids)
        self._raise_on_degenerate_author(clean_book_ids, name=name)
        with transaction.atomic():
            orm_author = self._create_without_relations(name=name)
            orm_author.books.add(*clean_book_ids)  # type: ignore
        author = Author.model_validate(orm_author)
        return author

    def delete(self, author_id: ID, /) -> None:
        try:
            record = OrmAuthor.objects.get(pk=author_id)
            record.delete()
        except OrmAuthor.DoesNotExist:
            pass

    def get_all(self, /) -> list[Author]:
        orm_authors = OrmAuthor.objects.prefetch_related("books").all()
        authors = [Author.model_validate(i) for i in orm_authors]
        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        author: Author | None
        try:
            orm_author = OrmAuthor.objects.get(name=name)
            author = Author.model_validate(orm_author)
        except OrmAuthor.DoesNotExist:
            author = None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author: Author | None
        try:
            orm_author = OrmAuthor.objects.get(pk=author_id)
            author = Author.model_validate(orm_author)
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
        current = OrmAuthor.objects.filter(pk=author_id).first()
        if not current:
            raise LostAuthorsError(author_ids=[author_id])

        if book_ids is not None:
            new_book_ids = self._clean_book_ids(book_ids)
            self._raise_on_degenerate_author(
                new_book_ids,
                author_id=current.pk,
                name=current.name,
            )

        with transaction.atomic():
            if name is not None and name != current.name:
                self._raise_on_duplicate_name(name)
                current.name = name
                current.save()

            if book_ids is not None:
                current.books.clear()
                current.books.add(*new_book_ids)  # type: ignore

        author = Author.model_validate(current)

        return author

    def _clean_book_ids(self, book_ids: Collection[ID], /) -> list[ID]:
        raw_book_ids = sorted(set(book_ids))
        books = OrmBook.objects.filter(pk__in=raw_book_ids).all()
        clean_book_ids = [i.pk for i in books]

        lost_book_ids = [i for i in raw_book_ids if i not in clean_book_ids]
        if lost_book_ids:
            raise LostBooksError(book_ids=lost_book_ids)

        return clean_book_ids

    def _create_without_relations(self, /, *, name: str) -> OrmAuthor:
        author_id = uuid4()
        orm_author = OrmAuthor(name=name, pk=author_id)
        orm_author.save()
        return orm_author

    def _raise_on_degenerate_author(
        self,
        book_ids: Collection[ID],
        /,
        *,
        name: str,
        author_id: ID | None = None,
    ) -> None:
        if book_ids:
            return

        raise DegenerateAuthorsError(authors={name: author_id})

    def _raise_on_duplicate_name(self, name: str, /) -> None:
        if OrmAuthor.objects.filter(name=name).exists():
            raise DuplicateAuthorNameError(name=name)


__all__ = ("AuthorRepo",)

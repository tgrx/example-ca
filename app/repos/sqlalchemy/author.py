from typing import Collection
from typing import final
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine

from app.entities.models import ID
from app.entities.models import Author
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books_authors


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    engine: Engine

    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        # todo: use book ids
        # todo: check book ids for lost
        assert book_ids
        author_id = uuid4()

        values = {
            table_authors.c.author_id: author_id,
            table_authors.c.name: name,
        }

        stmt = (
            sa.insert(table_authors)
            .values(values)
            .returning(
                table_authors.c.author_id,
                table_authors.c.name,
            )
        )

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            row = cursor.fetchone()

        author = Author.model_validate(row)

        return author

    def delete(self, author_id: ID, /) -> None:
        stmt_books_authors = table_books_authors.delete().where(
            table_books_authors.c.author_id == author_id,
        )

        stmt_authors = table_authors.delete().where(
            table_authors.c.author_id == author_id,
        )

        conn: Connection
        with self.engine.begin() as conn:
            conn.execute(stmt_books_authors)
            conn.execute(stmt_authors)

    def get_all(self, /) -> list[Author]:
        stmt = self.__stmt_all_authors()

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            authors = [Author.model_validate(row) for row in cursor]

        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        stmt = self.__stmt_all_authors().where(table_authors.c.name == name)

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            author = Author.model_validate(row) if row else None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        stmt = self.__stmt_all_authors().where(
            table_authors.c.author_id == author_id,
        )

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            author = Author.model_validate(row) if row else None

        return author

    def update(
        self,
        author_id: ID,
        /,
        *,
        book_ids: Collection[ID] | None = None,
        name: str | None = None,
    ) -> Author:
        # todo: use book ids
        assert book_ids
        values = {table_authors.c.name: name}
        stmt = (
            sa.update(table_authors)
            .values(values)
            .where(table_authors.c.author_id == author_id)
            .returning(
                table_authors.c.author_id,
                table_authors.c.name,
            )
        )

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            assert row is not None
            author = Author.model_validate(row)

        return author

    @staticmethod
    def __stmt_all_authors() -> sa.Select:
        stmt = table_authors.select().order_by(
            table_authors.c.name.asc(),
            table_authors.c.author_id.asc(),
        )

        return stmt


__all__ = ("AuthorRepo",)

from typing import TYPE_CHECKING
from uuid import uuid4

import attrs
from sqlalchemy.dialects.postgresql import insert

from app.entities.models import Author
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books_authors

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy import Connection
    from sqlalchemy import Engine


@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    engine: "Engine"

    def create(
        self,
        *,
        name: str,
    ) -> "Author":
        stmt = (
            insert(table_authors)
            .values(
                id=uuid4(),
                name=name,
            )
            .returning(
                table_authors.c.id,
                table_authors.c.name,
            )
        )

        conn: "Connection"
        with self.engine.begin() as conn:
            # todo: what if obj already exist, or another integrity error?
            # todo: what if db is down?
            cursor = conn.execute(stmt)
            row = cursor.fetchone()

        author = Author.model_validate(row)

        return author

    def delete(
        self,
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        stmt_books_authors = table_books_authors.delete().where(
            table_books_authors.c.author_id == id,
        )
        stmt_authors = table_authors.delete().where(
            table_authors.c.id == id,
        )

        conn: "Connection"
        with self.engine.begin() as conn:
            # todo: what if db is down?
            conn.execute(stmt_books_authors)
            conn.execute(stmt_authors)

    def get_all(self) -> list["Author"]:
        stmt = table_authors.select().order_by(
            table_authors.c.name.asc(),
        )

        conn: "Connection"
        with self.engine.begin() as conn:
            # todo: what if db is down?
            cursor = conn.execute(stmt)
            authors = [Author.model_validate(row) for row in cursor]

        return authors


__all__ = ("AuthorRepo",)

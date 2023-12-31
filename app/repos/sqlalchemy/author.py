from typing import Collection
from typing import cast
from typing import final
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import aggregate_order_by

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateAuthorNameError
from app.entities.errors import LostAuthorsError
from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import to_uuid
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    engine: Engine

    def create(self, /, *, book_ids: Collection[ID], name: str) -> Author:
        conn: Connection
        with self.engine.begin() as conn:
            self._raise_on_duplicate_name(conn, name)
            clean_book_ids = self._clean_book_ids(conn, book_ids)
            self._raise_on_degenerate_author(clean_book_ids, name=name)
            author_id = self._create_without_relations(conn, name=name)
            self._assing_books(conn, author_id, clean_book_ids)

        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorsError(author_ids=[author_id])

        return author

    def delete(self, author_id: ID, /) -> None:
        conn: Connection
        with self.engine.begin() as conn:
            self._unassign_books(conn, author_id)
            self._delete(conn, author_id)

    def get_all(self, /) -> list[Author]:
        sql = self.__build_total_sql()
        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(sql)
            authors = [Author.model_validate(row) for row in cursor]

        return authors

    def get_by_id(self, author_id: ID, /) -> Author | None:
        stmt = self.__build_total_sql().where(
            table_authors.c.author_id == author_id,
        )

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            author = Author.model_validate(row) if row else None

        return author

    def get_by_name(self, name: str, /) -> Author | None:
        sql = self.__build_total_sql().where(table_authors.c.name == name)
        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(sql)
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
        current = self.get_by_id(author_id)
        if current is None:
            raise LostAuthorsError(author_ids=[author_id])

        if name is None and book_ids is None:
            return current

        conn: Connection
        with self.engine.begin() as conn:
            if name is not None and name != current.name:
                self._raise_on_duplicate_name(conn, name)
                self._update_without_relations(
                    conn,
                    current.author_id,
                    name=name,
                )

            if book_ids is not None and book_ids != current.book_ids:
                clean_book_ids = self._clean_book_ids(conn, book_ids)
                self._raise_on_degenerate_author(
                    clean_book_ids,
                    author_id=author_id,
                    name=current.name,
                )
                self._unassign_books(conn, author_id)
                self._assing_books(conn, author_id, clean_book_ids)

        author = self.get_by_id(author_id)
        if author is None:
            raise LostAuthorsError(author_ids=[author_id])

        return author

    def _assing_books(
        self,
        conn: Connection,
        author_id: ID,
        book_ids: list[ID],
        /,
    ) -> None:
        values = [
            {
                table_books_authors.c.author_id: author_id,
                table_books_authors.c.book_id: book_id,
            }
            for book_id in book_ids
        ]
        sql = sa.insert(table_books_authors).values(values)
        conn.execute(sql)

    def _clean_book_ids(
        self,
        conn: Connection,
        book_ids: Collection[ID],
        /,
    ) -> list[ID]:
        if not book_ids:
            return []

        sql = (
            sa.select(
                table_books.c.book_id,
            )
            .where(table_books.c.book_id.in_(book_ids))
            .order_by(
                table_books.c.title.asc(),
            )
        )

        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        clean_book_ids = [row.book_id for row in rows]
        return clean_book_ids

    def _create_without_relations(
        self,
        conn: Connection,
        /,
        *,
        name: str,
    ) -> ID:
        sql = (
            sa.insert(table_authors)
            .values(
                {
                    table_authors.c.author_id: uuid4(),
                    table_authors.c.name: name,
                }
            )
            .returning(
                table_authors.c.author_id,
            )
        )

        author_id_raw = cast(ID, conn.execute(sql).scalar())
        author_id = to_uuid(author_id_raw)

        return author_id

    def _delete(self, conn: Connection, author_id: ID, /) -> None:
        sql = table_authors.delete().where(
            table_authors.c.author_id == author_id,
        )
        conn.execute(sql)

    def _raise_on_degenerate_author(
        self,
        book_ids: Collection[ID],
        /,
        *,
        name: str,
        author_id: ID | None = None,
    ) -> None:
        if not book_ids:
            raise DegenerateAuthorsError(authors={name: author_id})

    def _raise_on_duplicate_name(self, conn: Connection, name: str, /) -> None:
        sql = sa.select(sa.exists().where(table_authors.c.name == name))
        name_is_taken = conn.execute(sql).scalar()
        if name_is_taken:
            raise DuplicateAuthorNameError(name=name)

    def _update_without_relations(
        self,
        conn: Connection,
        author_id: ID,
        /,
        *,
        name: str,
    ) -> None:
        sql = (
            sa.update(table_authors)
            .values(
                {
                    table_authors.c.name: name,
                }
            )
            .where(table_authors.c.author_id == author_id)
        )
        conn.execute(sql)

    def _unassign_books(self, conn: Connection, author_id: ID, /) -> None:
        sql = table_books_authors.delete().where(
            table_books_authors.c.author_id == author_id,
        )
        conn.execute(sql)

    @staticmethod
    def __build_total_sql() -> sa.Select:
        stmt = (  # noqa: ECE001
            sa.select(
                table_authors.c.author_id,
                table_authors.c.name,
                sa.func.coalesce(
                    sa.func.array_agg(
                        aggregate_order_by(  # type: ignore
                            table_books.c.book_id,
                            table_books.c.title.asc(),
                        ),
                    ).filter(
                        ~table_books.c.book_id.is_(None),
                    ),
                    [],
                ).label("book_ids"),
            )
            .select_from(
                table_authors,
            )
            .join(
                table_books_authors,
                table_books_authors.c.author_id == table_authors.c.author_id,
            )
            .join(
                table_books,
                table_books.c.book_id == table_books_authors.c.book_id,
            )
            .group_by(
                table_authors.c.author_id,
            )
            .order_by(
                table_authors.c.name,
            )
        )

        return stmt


__all__ = ("AuthorRepo",)

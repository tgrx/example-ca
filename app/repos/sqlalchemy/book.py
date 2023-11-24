from typing import Collection
from typing import final
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.dialects.postgresql import insert

from app.entities.models import ID
from app.entities.models import Book
from app.entities.models import to_uuid
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    engine: Engine

    def create(self, /, *, author_ids: Collection[ID], title: str) -> Book:
        conn: Connection
        with self.engine.begin() as conn:
            book_id = self._create_book_without_relations(conn, title=title)
            self._assign_authors(conn, book_id, author_ids=author_ids)
            book = self._get_by_id(conn, book_id)

        return book

    def delete(self, book_id: ID, /) -> None:
        stmt_books_authors = table_books_authors.delete().where(
            table_books_authors.c.book_id == book_id,
        )
        stmt_books = table_books.delete().where(
            table_books.c.book_id == book_id,
        )

        conn: Connection
        with self.engine.begin() as conn:
            # todo: what if db is down?
            conn.execute(stmt_books_authors)
            conn.execute(stmt_books)

    def get_all(self, /) -> list[Book]:
        stmt = self.__stmt_all_books()

        conn: Connection
        with self.engine.begin() as conn:
            # todo: what if db is down?
            cursor = conn.execute(stmt)
            books = [Book.model_validate(row) for row in cursor]

        return books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        conn: Connection
        with self.engine.begin() as conn:
            book = self._get_by_id(conn, book_id)

        return book

    def get_by_title(self, title: str, /) -> Book | None:
        stmt = (
            self.__stmt_all_books()
            .where(table_books.c.title == title)
            .limit(1)
        )

        conn: Connection
        with self.engine.begin() as conn:
            # todo: what if db is down?
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            book = Book.model_validate(row) if row else None

        return book

    def update(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        conn: Connection
        with self.engine.begin() as conn:
            if title is not None:
                self._update_book(conn, book_id, title=title)

            if author_ids is not None:
                self._assign_authors(conn, book_id, author_ids=author_ids)

            book = self._get_by_id(conn, book_id)

        return book

    def _assign_authors(
        self,
        conn: Connection,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID],
    ) -> None:
        author_ids = sorted(set(author_ids))

        values = [
            {
                table_books_authors.c.author_id: author_id,
                table_books_authors.c.book_id: book_id,
            }
            for author_id in author_ids
        ]

        stmt = insert(table_books_authors).values(values)
        conn.execute(stmt)

    def _create_book_without_relations(
        self,
        conn: Connection,
        /,
        *,
        title: str,
    ) -> ID:
        book_id = uuid4()
        values = {table_books.c.book_id: book_id, table_books.c.title: title}
        stmt = (
            insert(table_books)
            .values(values)
            .returning(
                table_books.c.book_id,
            )
        )

        cursor = conn.execute(stmt)
        row = cursor.fetchone()

        assert row is not None, "no results returned after creating a book"
        book_id = to_uuid(row.book_id)

        return book_id

    def _get_by_id(self, conn: Connection, book_id: ID, /) -> Book:
        stmt = (
            self.__stmt_all_books()
            .where(table_books.c.book_id == book_id)
            .limit(1)
        )

        cursor = conn.execute(stmt)
        row = cursor.fetchone()
        book = Book.model_validate(row)

        return book

    def _update_book(
        self,
        conn: Connection,
        book_id: ID,
        /,
        *,
        title: str,
    ) -> None:
        values = {table_books.c.title: title}

        stmt = (
            sa.update(table_books)
            .values(values)
            .where(table_books.c.book_id == book_id)
        )

        conn.execute(stmt)

    @staticmethod
    def __stmt_all_books() -> sa.Select:
        stmt = (  # noqa: ECE001
            sa.select(
                table_books.c.book_id,
                table_books.c.title,
                sa.func.json_agg(
                    aggregate_order_by(  # type: ignore
                        sa.func.json_build_object(
                            "author_id",
                            sa.cast(table_authors.c.author_id, sa.UUID),
                            "name",
                            table_authors.c.name,
                        ),
                        table_authors.c.name.asc(),
                        table_authors.c.author_id.asc(),
                    ),
                ).label("authors"),
            )
            .select_from(
                table_books,
            )
            .outerjoin(
                table_books_authors,
                table_books_authors.c.book_id == table_books.c.book_id,
            )
            .outerjoin(
                table_authors,
                table_authors.c.author_id == table_books_authors.c.author_id,
            )
            .order_by(
                table_books.c.title,
                table_books.c.book_id,
            )
            .group_by(
                table_books.c.book_id,
            )
        )

        return stmt


__all__ = ("BookRepo",)

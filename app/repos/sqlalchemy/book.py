from typing import Collection
from typing import final
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import aggregate_order_by

from app.entities.models import ID
from app.entities.models import Author
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

        assert book is not None

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
            books = [
                book
                for book in (
                    self.__row_to_book(row)
                    for row in cursor
                    if row is not None
                )
                if book is not None
            ]

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
            book = self.__row_to_book(row)

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

        assert book is not None

        return book

    def _assign_authors(
        self,
        conn: Connection,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID],
    ) -> None:
        statements: list[sa.Insert | sa.Delete] = [
            sa.delete(table_books_authors).where(
                table_books_authors.c.book_id == book_id,
            )
        ]

        if author_ids:
            statements.append(
                sa.insert(table_books_authors).values(
                    [
                        {
                            table_books_authors.c.author_id: author_id,
                            table_books_authors.c.book_id: book_id,
                        }
                        for author_id in author_ids
                    ]
                )
            )

        for stmt in statements:
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
            sa.insert(table_books)
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

    def _get_by_id(self, conn: Connection, book_id: ID, /) -> Book | None:
        stmt = (
            self.__stmt_all_books()
            .where(table_books.c.book_id == book_id)
            .limit(1)
        )

        cursor = conn.execute(stmt)
        row = cursor.fetchone()
        book = self.__row_to_book(row)

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
    def __row_to_book(row: sa.Row | None, /) -> Book | None:
        if not row:
            return None

        book = Book(
            authors=[Author.model_validate(obj) for obj in row.authors or []],
            book_id=to_uuid(row.book_id),
            title=row.title,
        )

        return book

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
                )
                .filter(
                    ~table_authors.c.author_id.is_(None),
                )
                .label("authors"),
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

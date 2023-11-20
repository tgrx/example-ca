from typing import TYPE_CHECKING
from typing import cast
from uuid import UUID
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.dialects.postgresql import insert

from app.entities.models import Book
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors

if TYPE_CHECKING:
    from sqlalchemy import Connection
    from sqlalchemy import Engine


@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    engine: "Engine"

    def create(
        self,
        *,
        author_ids: list["UUID"],
        title: str,
    ) -> "Book":
        conn: "Connection"
        with self.engine.begin() as conn:
            book_id = self._create_book_without_relations(
                conn,
                title=title,
            )
            self._assign_authors_on_book(
                conn,
                author_ids=author_ids,
                book_id=book_id,
            )
            book = self._get_book_by_id(
                conn,
                id=book_id,
            )
        return book

    def delete(
        self,
        id: "UUID",  # noqa: A002,VNE003
    ) -> None:
        stmt_books_authors = table_books_authors.delete().where(
            table_books_authors.c.book_id == id,
        )
        stmt_books = table_books.delete().where(
            table_books.c.id == id,
        )

        conn: "Connection"
        with self.engine.begin() as conn:
            # todo: what if db is down?
            conn.execute(stmt_books_authors)
            conn.execute(stmt_books)

    def get_all(self) -> list["Book"]:
        stmt = self.__stmt_all_books()

        conn: "Connection"
        with self.engine.begin() as conn:
            # todo: what if db is down?
            cursor = conn.execute(stmt)
            books = [Book.model_validate(row) for row in cursor]

        return books

    def update(
        self,
        id: "UUID",  # noqa: A002,VNE003
        *,
        # todo: #6 use undefined as default
        author_ids: list["UUID"] | None = None,
        # todo: #6 use undefined as default
        title: str | None = None,
    ) -> "Book":
        conn: "Connection"
        with self.engine.begin() as conn:
            if title is not None:
                self._update_book(
                    conn,
                    id,
                    title=title,
                )
            if author_ids is not None:
                self._assign_authors_on_book(
                    conn,
                    author_ids=author_ids,
                    book_id=id,
                )
            book = self._get_book_by_id(
                conn,
                id=id,
            )

        return book

    def _assign_authors_on_book(
        self,
        conn: "Connection",
        book_id: "UUID",
        author_ids: list["UUID"],
    ) -> None:
        values = [
            {"book_id": book_id, "author_id": author_id}
            for author_id in author_ids
        ]
        stmt = insert(table_books_authors).values(values)
        conn.execute(stmt)

    def _create_book_without_relations(
        self,
        conn: "Connection",
        *,
        title: str,
    ) -> "UUID":
        stmt = (
            insert(table_books)
            .values(
                id=uuid4(),
                title=title,
            )
            .returning(
                table_books.c.id,
            )
        )

        cursor = conn.execute(stmt)
        row = cursor.fetchone()

        assert row is not None, "no results returned after creating a book"
        book_id = cast(UUID, row.id)

        return book_id

    def _get_book_by_id(
        self,
        conn: "Connection",
        *,
        id: "UUID",  # noqa: A002
    ) -> "Book":
        stmt = self.__stmt_all_books().where(
            table_books.c.id == id,
        )

        cursor = conn.execute(stmt)
        row = cursor.fetchone()
        book = Book.model_validate(row)

        return book

    def _update_book(
        self,
        conn: "Connection",
        id: "UUID",  # noqa: A002,VNE003
        title: str,
    ) -> None:
        stmt = (
            sa.update(table_books)
            .values(
                title=title,
            )
            .where(table_books.c.id == id)
        )
        conn.execute(stmt)

    @staticmethod
    def __stmt_all_books() -> sa.Select:
        stmt = (  # noqa: ECE001
            sa.select(
                table_books.c.id,
                table_books.c.title,
                sa.func.json_agg(
                    aggregate_order_by(  # type: ignore
                        sa.func.json_build_object(
                            "id",
                            sa.cast(table_authors.c.id, sa.UUID),
                            "name",
                            table_authors.c.name,
                        ),
                        table_authors.c.name,
                        table_authors.c.id,
                    ),
                ).label("authors"),
            )
            .select_from(
                table_books,
            )
            .outerjoin(
                table_books_authors,
                table_books_authors.c.book_id == table_books.c.id,
            )
            .outerjoin(
                table_authors,
                table_authors.c.id == table_authors.c.id,
            )
            .order_by(
                table_books.c.title,
                table_books.c.id,
            )
            .group_by(
                table_books.c.id,
            )
        )

        return stmt


__all__ = ("BookRepo",)

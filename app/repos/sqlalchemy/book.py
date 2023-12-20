from typing import Collection
from typing import final
from uuid import uuid4

import attrs
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import aggregate_order_by

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
from app.entities.models import ID
from app.entities.models import Book
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors


@final
@attrs.frozen(kw_only=True, slots=True)
class BookRepo:
    engine: Engine

    def create(self, /, *, title: str) -> Book:
        existing = self.get_by_title(title)
        if existing is not None:
            raise DuplicateBookTitleError(title=title)

        book_id = uuid4()

        conn: Connection
        with self.engine.begin() as conn:
            stmt = sa.insert(table_books).values(
                {
                    table_books.c.book_id: book_id,
                    table_books.c.title: title,
                }
            )
            conn.execute(stmt)

        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        return book

    def delete(self, book_id: ID, /) -> None:
        conn: Connection
        with self.engine.begin() as conn:
            stmt = (
                sa.select(table_authors.c.author_id)
                .select_from(
                    table_books,
                    table_books_authors,
                    table_authors,
                )
                .where(
                    sa.and_(
                        table_books.c.book_id == table_books_authors.c.book_id,
                        table_authors.c.author_id
                        == table_books_authors.c.author_id,
                        table_books.c.book_id == book_id,
                    )
                )
            )
            rows = conn.execute(stmt).fetchall()
            author_ids = [row.author_id for row in rows]
            if author_ids:
                stmt = (  # noqa: ECE001
                    sa.select(
                        table_authors.c.author_id,
                        table_authors.c.name,
                        sa.func.count(table_books_authors.c.book_id).label(
                            "nr_books"
                        ),
                    )
                    .select_from(
                        table_authors,
                    )
                    .outerjoin(
                        table_books_authors,
                        sa.and_(
                            table_books_authors.c.author_id
                            == table_authors.c.author_id,
                            table_books_authors.c.book_id != book_id,
                        ),
                    )
                    .where(table_authors.c.author_id.in_(author_ids))
                    .group_by(table_authors.c.author_id)
                )
                rows = conn.execute(stmt).fetchall()
                degenerates = {
                    row.name: row.author_id for row in rows if not row.nr_books
                }
                if degenerates:
                    raise DegenerateAuthorsError(authors=degenerates)

        with self.engine.begin() as conn:
            stmt_books_authors = table_books_authors.delete().where(
                table_books_authors.c.book_id == book_id,
            )
            conn.execute(stmt_books_authors)
            stmt_books = table_books.delete().where(
                table_books.c.book_id == book_id,
            )
            conn.execute(stmt_books)

    def get_all(self, /) -> list[Book]:
        stmt = self.__stmt_all_books()

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(stmt)
            rows = cursor.fetchall()
            books = [Book.model_validate(row) for row in rows]

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
            cursor = conn.execute(stmt)
            row = cursor.fetchone()
            if not row:
                return None
            book = Book.model_validate(row)

        return book

    def update(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        existing = self.get_by_id(book_id)
        if existing is None:
            raise LostBooksError(book_ids=[book_id])

        conn: Connection
        with self.engine.begin() as conn:
            if title is not None and title != existing.title:
                existing_with_title = self.get_by_title(title)
                if existing_with_title is not None:
                    raise DuplicateBookTitleError(title=title)

                stmt = (
                    sa.update(table_books)
                    .values(
                        {
                            table_books.c.title: title,
                        }
                    )
                    .where(
                        table_books.c.book_id == book_id,
                    )
                )
                conn.execute(stmt)

            if author_ids is not None:
                self._assign_authors(conn, book_id, author_ids=author_ids)

        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        return book

    def _assign_authors(
        self,
        conn: Connection,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID],
    ) -> None:
        existing = self.get_by_id(book_id)
        if existing is None:
            raise LostBooksError(book_ids=[book_id])

        clean_author_ids = set(self._clean_author_ids(conn, author_ids))
        discarded_author_ids = set(existing.author_ids) - clean_author_ids

        stmt = (  # noqa: ECE001
            sa.select(
                table_authors.c.author_id,
                table_authors.c.name,
                sa.func.count(table_books_authors.c.book_id).label("nr_books"),
            )
            .select_from(
                table_authors,
            )
            .outerjoin(
                table_books_authors,
                sa.and_(
                    table_books_authors.c.author_id
                    == table_authors.c.author_id,
                    table_books_authors.c.book_id != book_id,
                ),
            )
            .where(table_authors.c.author_id.in_(discarded_author_ids))
            .group_by(table_authors.c.author_id)
        )
        rows = conn.execute(stmt).fetchall()
        degenerates = {
            row.name: row.author_id for row in rows if not row.nr_books
        }
        if degenerates:
            raise DegenerateAuthorsError(authors=degenerates)

        statements: list = [
            sa.delete(table_books_authors).where(
                table_books_authors.c.book_id == book_id,
            ),
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

    def _clean_author_ids(
        self,
        conn: Connection,
        author_ids: Collection[ID],
        /,
    ) -> list[ID]:
        if not author_ids:
            return []

        stmt = sa.select(table_authors.c.author_id).where(
            table_authors.c.author_id.in_(author_ids)
        )
        rows = conn.execute(stmt).fetchall()
        actual_author_ids = [row.author_id for row in rows]
        lost_author_ids = set(author_ids) - set(actual_author_ids)
        if lost_author_ids:
            raise LostAuthorsError(author_ids=lost_author_ids)

        return actual_author_ids

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

    @staticmethod
    def __row_to_book(row: sa.Row | None, /) -> Book | None:
        if not row:
            return None

        book = Book.model_validate(row)

        return book

    @staticmethod
    def __stmt_all_books() -> sa.Select:
        stmt = (  # noqa: ECE001
            sa.select(
                table_books.c.book_id,
                table_books.c.title,
                sa.func.coalesce(
                    sa.func.array_agg(
                        aggregate_order_by(  # type: ignore
                            table_authors.c.author_id,
                            table_authors.c.name.asc(),
                        ),
                    ).filter(
                        ~table_authors.c.author_id.is_(None),
                    ),
                    [],
                ).label("author_ids"),
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
                table_books.c.title.asc(),
                table_books.c.book_id.asc(),
            )
            .group_by(
                table_books.c.book_id,
            )
        )

        return stmt


__all__ = ("BookRepo",)

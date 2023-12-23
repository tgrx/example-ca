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
from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
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

    def create(self, /, *, title: str) -> Book:
        conn: Connection
        with self.engine.begin() as conn:
            self._raise_on_duplicate_title(conn, title)
            book_id = self._create_without_relations(conn, title=title)

        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        return book

    def delete(self, book_id: ID, /) -> None:
        current = self.get_by_id(book_id)
        if current is None:
            return

        conn: Connection
        with self.engine.begin() as conn:
            self._raise_on_degenerate_authors(
                conn,
                book_id,
                current.author_ids,
            )
            self._unassign_authors(conn, book_id)
            self._delete(conn, book_id)

    def get_all(self, /) -> list[Book]:
        sql = self.__build_all_sql()

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            books = [Book.model_validate(row) for row in rows]

        return books

    def get_by_id(self, book_id: ID, /) -> Book | None:
        sql = (
            self.__build_all_sql()
            .where(table_books.c.book_id == book_id)
            .limit(1)
        )

        conn: Connection
        with self.engine.begin() as conn:
            cursor = conn.execute(sql)
            row = cursor.fetchone()
            book = Book.model_validate(row) if row else None

        return book

    def get_by_title(self, title: str, /) -> Book | None:
        stmt = (
            self.__build_all_sql()
            .where(
                table_books.c.title == title,
            )
            .limit(1)
        )

        conn: Connection
        with self.engine.begin() as conn:
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
        current = self.get_by_id(book_id)
        if current is None:
            raise LostBooksError(book_ids=[book_id])

        conn: Connection
        with self.engine.begin() as conn:
            if title is not None and title != current.title:
                self._raise_on_duplicate_title(conn, title)
                self._update_without_relations(conn, book_id, title=title)

            if author_ids is not None and author_ids != current.author_ids:
                clean_author_ids = self._clean_author_ids(conn, author_ids)
                discard_author_ids = set(current.author_ids)
                discard_author_ids -= set(clean_author_ids)
                self._raise_on_degenerate_authors(
                    conn,
                    book_id,
                    discard_author_ids,
                )
                self._unassign_authors(conn, book_id)
                self._assign_authors(conn, book_id, clean_author_ids)

        book = self.get_by_id(book_id)
        if book is None:
            raise LostBooksError(book_ids=[book_id])

        return book

    def _assign_authors(
        self,
        conn: Connection,
        book_id: ID,
        author_ids: Collection[ID],
        /,
    ) -> None:
        if not author_ids:
            return

        values = [
            {
                table_books_authors.c.author_id: author_id,
                table_books_authors.c.book_id: book_id,
            }
            for author_id in author_ids
        ]

        sql = sa.insert(table_books_authors).values(values)

        conn.execute(sql)

    def _clean_author_ids(
        self,
        conn: Connection,
        author_ids: Collection[ID],
        /,
    ) -> list[ID]:
        if not author_ids:
            return []

        sql = (
            sa.select(
                table_authors.c.author_id,
            )
            .where(
                table_authors.c.author_id.in_(author_ids),
            )
            .order_by(
                table_authors.c.name,
            )
        )

        rows = conn.execute(sql).fetchall()
        actual_author_ids = [row.author_id for row in rows]

        lost_author_ids = set(author_ids) - set(actual_author_ids)
        if lost_author_ids:
            raise LostAuthorsError(author_ids=lost_author_ids)

        return actual_author_ids

    def _create_without_relations(
        self, conn: Connection, /, *, title: str
    ) -> ID:
        sql = (
            sa.insert(table_books)
            .values(
                {
                    table_books.c.book_id: uuid4(),
                    table_books.c.title: title,
                }
            )
            .returning(
                table_books.c.book_id,
            )
        )

        book_id_raw = cast(ID, conn.execute(sql).scalar())
        book_id = to_uuid(book_id_raw)

        return book_id

    def _delete(self, conn: Connection, book_id: ID) -> None:
        sql = sa.delete(
            table_books,
        ).where(
            table_books.c.book_id == book_id,
        )

        conn.execute(sql)

    def _raise_on_degenerate_authors(
        self,
        conn: Connection,
        book_id: ID,
        author_ids: Collection[ID],
        /,
    ) -> None:
        if not author_ids:
            return

        authors = table_authors
        m2m = table_books_authors

        sql = (  # noqa: ECE001
            sa.select(
                authors.c.author_id,
                authors.c.name,
                sa.func.count(m2m.c.book_id).label("nr_books"),
            )
            .select_from(
                authors,
            )
            .outerjoin(
                m2m,
                sa.and_(
                    m2m.c.author_id == authors.c.author_id,
                    m2m.c.book_id != book_id,
                ),
            )
            .where(
                authors.c.author_id.in_(author_ids),
            )
            .group_by(
                authors.c.author_id,
            )
        )

        rows = conn.execute(sql).fetchall()

        degenerates = {
            row.name: row.author_id for row in rows if not row.nr_books
        }

        if degenerates:
            raise DegenerateAuthorsError(authors=degenerates)

    def _raise_on_duplicate_title(
        self,
        conn: Connection,
        title: str,
        /,
    ) -> None:
        sql = sa.select(
            sa.exists().where(
                table_books.c.title == title,
            )
        )

        title_is_taken = conn.execute(sql).scalar()
        if title_is_taken:
            raise DuplicateBookTitleError(title=title)

    def _unassign_authors(self, conn: Connection, book_id: ID, /) -> None:
        sql = sa.delete(
            table_books_authors,
        ).where(
            table_books_authors.c.book_id == book_id,
        )

        conn.execute(sql)

    def _update_without_relations(
        self,
        conn: Connection,
        book_id: ID,
        /,
        *,
        title: str,
    ) -> None:
        sql = (
            sa.update(
                table_books,
            )
            .values(
                {
                    table_books.c.title: title,
                }
            )
            .where(
                table_books.c.book_id == book_id,
            )
        )
        conn.execute(sql)

    @staticmethod
    def __build_all_sql() -> sa.Select:
        authors = table_authors
        books = table_books
        m2m = table_books_authors

        sql = (  # noqa: ECE001
            sa.select(
                books.c.book_id,
                books.c.title,
                sa.func.coalesce(
                    sa.func.array_agg(
                        aggregate_order_by(  # type: ignore
                            authors.c.author_id,
                            authors.c.name.asc(),
                        ),
                    ).filter(
                        ~authors.c.author_id.is_(None),
                    ),
                    [],
                ).label("author_ids"),
            )
            .select_from(
                books,
            )
            .outerjoin(
                m2m,
                m2m.c.book_id == books.c.book_id,
            )
            .outerjoin(
                authors,
                authors.c.author_id == m2m.c.author_id,
            )
            .order_by(
                books.c.title.asc(),
                books.c.book_id.asc(),
            )
            .group_by(
                books.c.book_id,
            )
        )

        return sql


__all__ = ("BookRepo",)

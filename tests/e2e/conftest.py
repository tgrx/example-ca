from typing import TYPE_CHECKING
from typing import Iterator
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine

from app.repos.sqlalchemy.author import AuthorRepo
from app.repos.sqlalchemy.book import BookRepo
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors

if TYPE_CHECKING:
    from sqlalchemy import Connection
    from sqlalchemy import Engine
    from sqlalchemy import Table

    from app.entities.config import Config
    from app.entities.models import Author


@pytest.fixture(scope="session")
def installed_authors(
    *,
    primary_database_engine: "Engine",
) -> Iterator[dict["UUID", "Author"]]:
    repo = AuthorRepo(engine=primary_database_engine)

    authors = [
        repo.create(name=name)
        for name in [
            "Alexander Pushkin",
            "Victor Pelevin",
        ]
    ]

    authors_map = {author.id: author for author in authors}

    yield authors_map

    for author_id in authors_map:
        repo.delete(id=author_id)


@pytest.fixture(scope="session")
def installed_authors_with_books(
    *,
    installed_authors: dict["UUID", "Author"],
    primary_database_engine: "Engine",
) -> Iterator[dict["UUID", "Author"]]:
    repo = BookRepo(engine=primary_database_engine)

    books = [
        repo.create(
            title=f"Bio of {author.name}",
            author_ids=[author.id],
        )
        for author in installed_authors.values()
    ]

    yield installed_authors

    for book in books:
        repo.delete(id=book.id)


@pytest.fixture(scope="session")
def primary_database_engine(
    *,
    config: "Config",
) -> "Engine":
    engine = create_engine(
        config.PRIMARY_DATABASE_URL,
        echo=config.MODE_DEBUG,
    )
    return engine


@pytest.fixture(autouse=True, scope="function")
def warden(
    *,
    primary_database_engine: "Engine",
    request: pytest.FixtureRequest,
) -> Iterator[None]:
    tables = {
        table_authors,
        table_books_authors,
        table_books,
    }

    conn: "Connection"
    with primary_database_engine.begin() as conn:
        ids_before_test = {table: get_all_ids(conn, table) for table in tables}

    yield

    with primary_database_engine.begin() as conn:
        ids_after_test = {table: get_all_ids(conn, table) for table in tables}

        errors = []

        for table in tables:
            before = ids_before_test[table]
            after = ids_after_test[table]
            if before != after:
                extra = sorted(after - before)
                ti = sa.inspect(table)
                msg = "\n".join(
                    (
                        f'"{ti.name}" changed after `{request.node.name}`:',
                        f"rows:    {len(before)} => {len(after)}",
                        f"extra:   {extra}",
                        f"missing: {sorted(before - after)}",
                    )
                )
                errors.append(msg)

                conn.execute(
                    sa.text(f"truncate {ti.name} restart identity cascade;")
                )

    if errors:
        msg = "\n\n".join(errors)
        raise AssertionError(msg)


def get_all_ids(conn: "Connection", table: "Table") -> frozenset[int | UUID]:
    stmt = sa.select(table.c.id)
    rows = conn.execute(stmt).fetchall()
    ids = frozenset(row.id for row in rows)
    return ids

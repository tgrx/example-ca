from typing import Iterator
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy import Engine
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import inspect

from app.entities.config import Config
from app.repos.sqlalchemy.tables import table_authors
from app.repos.sqlalchemy.tables import table_books
from app.repos.sqlalchemy.tables import table_books_authors


@pytest.fixture(scope="session")
def primary_database_engine(*, config: Config) -> Engine:
    engine = create_engine(config.PRIMARY_DATABASE_URL, echo=config.MODE_DEBUG)

    return engine


@pytest.fixture(autouse=True, scope="function")
def warden(
    *,
    primary_database_engine: Engine,
    request: pytest.FixtureRequest,
) -> Iterator[None]:
    tables = {
        table_authors,
        table_books_authors,
        table_books,
    }

    conn: Connection
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


def get_all_ids(conn: Connection, table: Table, /) -> frozenset[int | UUID]:
    pk = inspect(table).primary_key.columns[0]
    stmt = sa.select(pk).select_from(table)
    rows = conn.execute(stmt).fetchall()
    ids = frozenset(row[0] for row in rows)

    return ids

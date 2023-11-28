from typing import Final

import sqlalchemy as sa

metadata: Final = sa.MetaData()

table_authors: Final = sa.Table(
    "authors",
    metadata,
    sa.Column(
        "author_id",
        sa.UUID(as_uuid=True),
        primary_key=True,
    ),
    sa.Column(
        "name",
        sa.Text(),
        nullable=False,
        unique=True,
    ),
)


table_books: Final = sa.Table(
    "books",
    metadata,
    sa.Column(
        "book_id",
        sa.UUID(as_uuid=True),
        primary_key=True,
    ),
    sa.Column(
        "title",
        sa.Text(),
        nullable=False,
        unique=True,
    ),
)

table_books_authors: Final = sa.Table(
    "books_authors",
    metadata,
    sa.Column(
        "author_id",
        sa.ForeignKey(
            table_authors.c.author_id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
    sa.Column(
        "book_id",
        sa.ForeignKey(
            table_books.c.book_id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
    sa.Column(
        "id",
        sa.BigInteger,
        autoincrement=True,
        primary_key=True,
    ),
)


__all__ = (
    "table_authors",
    "table_books_authors",
    "table_books",
)

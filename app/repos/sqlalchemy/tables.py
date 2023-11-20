import sqlalchemy as sa

metadata = sa.MetaData()

table_authors = sa.Table(
    "authors",
    metadata,
    sa.Column(
        "id",
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


table_books = sa.Table(
    "books",
    metadata,
    sa.Column(
        "id",
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

table_books_authors = sa.Table(
    "books_authors",
    metadata,
    sa.Column(
        "author_id",
        sa.ForeignKey(
            table_authors.c.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
    sa.Column(
        "book_id",
        sa.ForeignKey(
            table_books.c.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    ),
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        autoincrement=True,
    ),
)


__all__ = (
    "table_authors",
    "table_books_authors",
    "table_books",
)

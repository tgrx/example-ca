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


__all__ = (
    "table_authors",
    "table_books",
)

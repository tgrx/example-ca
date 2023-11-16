from typing import TYPE_CHECKING
from typing import Iterator

import pytest
from sqlalchemy import create_engine

from app.repos.sqlalchemy.author import AuthorRepo

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy import Engine

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
def primary_database_engine(
    *,
    config: "Config",
) -> "Engine":
    engine = create_engine(
        config.PRIMARY_DATABASE_URL,
        echo=True,
    )
    return engine

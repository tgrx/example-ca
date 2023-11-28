from typing import final
from uuid import uuid4

import attrs

from app.entities.models import ID
from app.entities.models import Author


@final
@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    index_authors: dict[ID, Author]

    def create(self, /, *, name: str) -> Author:
        author_id = uuid4()
        author = Author(author_id=author_id, name=name)
        self.index_authors[author_id] = author

        return author

    def delete(self, author_id: ID, /) -> None:
        self.index_authors.pop(author_id, ...)

    def get_all(self, /) -> list[Author]:
        authors = list(self.index_authors.values())

        return authors

    def get_by_name(self, name: str, /) -> Author | None:
        for author in self.index_authors.values():
            if author.name == name:
                break
        else:
            author = None

        return author

    def get_by_id(self, author_id: ID, /) -> Author | None:
        author = self.index_authors.get(author_id)

        return author

    def update(self, author_id: ID, /, *, name: str) -> Author:
        author = self.index_authors[author_id]
        author = author.model_copy(update={"name": name})
        self.index_authors[author.author_id] = author

        return author


__all__ = ("AuthorRepo",)

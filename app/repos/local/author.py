from typing import TYPE_CHECKING
from uuid import uuid4

import attrs

from app.entities.models import Author

if TYPE_CHECKING:
    from uuid import UUID


@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    storage: dict["UUID", "Author"] = attrs.field(factory=dict)

    def create(
        self,
        *,
        name: str,
    ) -> "Author":
        author = Author(
            id=uuid4(),
            name=name,
        )
        self.storage[author.id] = author

        return author

    def delete(
        self,
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        self.storage.pop(id, None)

    def get_all(self) -> list["Author"]:
        authors = list(self.storage.values())
        return authors

    def update(
        self,
        *,
        id: "UUID",  # noqa: A002
        name: str,
    ) -> "Author":
        author = self.storage[id]
        author = author.model_copy(update={"name": name})
        self.storage[author.id] = author
        return author


__all__ = ("AuthorRepo",)

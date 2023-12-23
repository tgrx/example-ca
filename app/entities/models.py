"""
This module contains models, or, data transfer objects (DTO).

Dataclasses: good.
Attrs: better.
Pydantic: best.
NamedTuple: hardcore.
"""

from typing import Annotated
from typing import final
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.functional_validators import BeforeValidator


def to_uuid(value: str | UUID, /) -> UUID:
    try:
        return value if isinstance(value, UUID) else UUID(value)
    except TypeError as err:
        raise ValueError(f"invalid uuid {value=!r}: {err}")


ID = Annotated[UUID, BeforeValidator(to_uuid)]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        frozen=True,
        loc_by_alias=True,
        strict=True,
    )


@final
class Author(Model):
    author_id: ID
    book_ids: list[ID]
    name: str


@final
class Book(Model):
    author_ids: list[ID]
    book_id: ID
    title: str


__all__ = (
    "Author",
    "Book",
)

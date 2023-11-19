"""
This module contains models, or, data transfer objects (DTO).

Dataclasses: good.
Attrs: better.
Pydantic: best.
NamedTuple: hardcore.
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict

default_model_config = ConfigDict(
    extra="forbid",
    from_attributes=True,
    frozen=True,
    loc_by_alias=True,
    strict=True,
)


class Author(BaseModel):
    model_config = default_model_config

    id: UUID  # noqa: A003,VNE003  # todo #6 rename
    name: str


class Book(BaseModel):
    model_config = default_model_config

    authors: list[Author]
    id: UUID  # noqa: A003,VNE003  # todo #6 rename
    title: str


__all__ = (
    "Author",
    "Book",
)

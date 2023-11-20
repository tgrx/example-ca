"""
This module contains models, or, data transfer objects (DTO).

Dataclasses: good.
Attrs: better.
Pydantic: best.
NamedTuple: hardcore.
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.functional_validators import BeforeValidator

default_model_config = ConfigDict(
    extra="forbid",
    from_attributes=True,
    frozen=True,
    loc_by_alias=True,
    strict=True,
)


def uuid_to_str(_value: str | UUID) -> UUID:
    return _value if isinstance(_value, UUID) else UUID(_value)


UUIDStr = Annotated[UUID, BeforeValidator(uuid_to_str)]


class Author(BaseModel):
    model_config = default_model_config

    id: UUIDStr  # noqa: A003,VNE003
    name: str


class Book(BaseModel):
    model_config = default_model_config

    authors: list[Author]
    id: UUIDStr  # noqa: A003,VNE003
    title: str


__all__ = (
    "Author",
    "Book",
)

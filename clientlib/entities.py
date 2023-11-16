from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict

from app.entities.models import Author

default_model_config = ConfigDict(
    extra="forbid",
    from_attributes=True,
    frozen=True,
    loc_by_alias=True,
    strict=True,
)


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    model_config = default_model_config

    data: T | None = None
    errors: list[str] | None = None


class AllAuthorsResponse(ApiResponse[list[Author]]):
    pass


class CreateAuthorRequest(BaseModel):
    model_config = default_model_config
    name: str


class CreateAuthorResponse(ApiResponse[Author]):
    pass


class GetAuthorResponse(ApiResponse[Author]):
    pass


__all__ = (
    "AllAuthorsResponse",
    "CreateAuthorRequest",
    "CreateAuthorResponse",
    "GetAuthorResponse",
)

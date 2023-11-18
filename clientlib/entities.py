from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict

from app.entities.models import Author
from app.entities.models import Book

default_model_config = ConfigDict(
    extra="forbid",
    from_attributes=True,
    frozen=True,
    loc_by_alias=True,
    strict=True,
)


T = TypeVar("T")


class ApiRequest(BaseModel):
    model_config = default_model_config


class ApiResponse(BaseModel, Generic[T]):
    model_config = default_model_config

    data: T | None = None
    errors: list[str] | None = None


class AllAuthorsResponse(ApiResponse[list[Author]]):
    pass


class AllBooksResponse(ApiResponse[list[Book]]):
    pass


class CreateAuthorRequest(ApiRequest):
    name: str


class CreateAuthorResponse(ApiResponse[Author]):
    pass


class CreateBookRequest(ApiRequest):
    authors: list[Author]
    title: str


class CreateBookResponse(ApiResponse[Book]):
    pass


class DeleteAuthorResponse(ApiResponse[None]):
    pass


class DeleteBookResponse(ApiResponse[None]):
    pass


class GetAuthorResponse(ApiResponse[Author]):
    pass


class GetBookResponse(ApiResponse[Book]):
    pass


class UpdateAuthorRequest(CreateAuthorRequest):
    pass


class UpdateAuthorResponse(ApiResponse[Author]):
    pass


class UpdateBookRequest(ApiRequest):
    authors: list[Author] | None = None
    title: str | None = None


class UpdateBookResponse(ApiResponse[Book]):
    pass


__all__ = (
    "AllAuthorsResponse",
    "AllBooksResponse",
    "CreateAuthorRequest",
    "CreateAuthorResponse",
    "CreateBookRequest",
    "CreateBookResponse",
    "DeleteAuthorResponse",
    "DeleteBookResponse",
    "GetAuthorResponse",
    "GetBookResponse",
    "UpdateAuthorRequest",
    "UpdateAuthorResponse",
    "UpdateBookRequest",
    "UpdateBookResponse",
)

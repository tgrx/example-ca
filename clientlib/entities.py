from typing import Generic
from typing import TypeVar
from typing import final

from pydantic import BaseModel
from pydantic import ConfigDict

from app.entities.models import ID
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


@final
class AllAuthorsResponse(ApiResponse[list[Author]]):
    pass


@final
class AllBooksResponse(ApiResponse[list[Book]]):
    pass


@final
class CreateAuthorRequest(ApiRequest):
    name: str


@final
class CreateAuthorResponse(ApiResponse[Author]):
    pass


@final
class CreateBookRequest(ApiRequest):
    authors: list[ID]
    title: str


@final
class CreateBookResponse(ApiResponse[Book]):
    pass


@final
class DeleteAuthorResponse(ApiResponse[None]):
    pass


@final
class DeleteBookResponse(ApiResponse[None]):
    pass


@final
class GetAuthorResponse(ApiResponse[Author]):
    pass


@final
class GetBookResponse(ApiResponse[Book]):
    pass


@final
class UpdateAuthorRequest(ApiRequest):
    name: str


@final
class UpdateAuthorResponse(ApiResponse[Author]):
    pass


@final
class UpdateBookRequest(ApiRequest):
    authors: list[ID] | None = None
    title: str | None = None


@final
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

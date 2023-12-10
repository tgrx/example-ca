from contextlib import suppress
from typing import Any
from typing import Callable
from typing import Collection
from typing import Type
from typing import TypeVar
from typing import cast
from typing import final

import attrs
import orjson
import tenacity
from httpx import Client
from httpx import Response
from pydantic import BaseModel

from app.entities.config import Config
from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from clientlib.entities import AllAuthorsResponse
from clientlib.entities import AllBooksResponse
from clientlib.entities import ApiResponse
from clientlib.entities import CreateAuthorRequest
from clientlib.entities import CreateAuthorResponse
from clientlib.entities import CreateBookRequest
from clientlib.entities import CreateBookResponse
from clientlib.entities import DeleteAuthorResponse
from clientlib.entities import DeleteBookResponse
from clientlib.entities import GetAuthorResponse
from clientlib.entities import GetBookResponse
from clientlib.entities import UpdateAuthorRequest
from clientlib.entities import UpdateAuthorResponse
from clientlib.entities import UpdateBookRequest
from clientlib.entities import UpdateBookResponse
from clientlib.errors import AppClientError

T = TypeVar("T")


def retry(config: Config) -> Callable:
    def decorator(func: Callable) -> Callable:
        if config.MODE_DEBUG:
            return func
        return tenacity.retry(
            stop=tenacity.stop_after_attempt(4),
            wait=tenacity.wait_exponential_jitter(
                exp_base=2,
                initial=1,
                jitter=1,
                max=10,
            ),
        )

    return decorator


@final
@attrs.frozen(kw_only=True, slots=True)
class AppClient:
    """
    The very first client of the whole app
    """

    config: Config
    session: Client

    def create_author(
        self,
        /,
        *,
        book_ids: Collection[ID],
        name: str,
    ) -> Author:
        book_ids = sorted(book_ids)
        req = CreateAuthorRequest(book_ids=book_ids, name=name)

        author = self._api_call(
            method="post",
            path="/api/v2/authors/",
            request=req,
            response_cls=CreateAuthorResponse,
            statuses=(201,),
        )

        return author

    def create_book(self, /, *, title: str) -> Book:
        req = CreateBookRequest(title=title)

        book = self._api_call(
            method="post",
            path="/api/v3/books/",
            request=req,
            response_cls=CreateBookResponse,
            statuses=(201,),
        )

        return book

    def delete_author_by_id(self, author_id: ID, /) -> None:
        return self._api_call(
            method="delete",
            path=f"/api/v2/authors/{author_id}/",
            response_cls=DeleteAuthorResponse,
        )

    def delete_book_by_id(self, book_id: ID, /) -> None:
        return self._api_call(
            method="delete",
            path=f"/api/v3/books/{book_id}/",
            response_cls=DeleteBookResponse,
        )

    def get_all_authors(self, /) -> list[Author]:
        authors = self._api_call(
            method="get",
            path="/api/v1/authors/",
            response_cls=AllAuthorsResponse,
        )

        return authors

    def get_all_books(self, /) -> list[Book]:
        books = self._api_call(
            method="get",
            path="/api/v3/books/",
            response_cls=AllBooksResponse,
        )

        return books

    def get_author_by_id(self, author_id: ID, /) -> Author:
        author = self._api_call(
            method="get",
            path=f"/api/v2/authors/{author_id}/",
            response_cls=GetAuthorResponse,
            statuses=(200, 404),
        )

        return author

    def get_author_by_name(self, name: str, /) -> Author:
        authors = self._api_call(
            method="get",
            params={"name": name},
            path="/api/v2/authors/",
            response_cls=AllAuthorsResponse,
        )

        if not authors:
            raise AppClientError(f"no author with {name=!r}")

        author = authors[0]

        return author

    def get_book_by_id(self, book_id: ID, /) -> Book:
        book = self._api_call(
            method="get",
            path=f"/api/v3/books/{book_id}/",
            response_cls=GetBookResponse,
            statuses=(200, 404),
        )

        return book

    def get_book_by_title(self, title: str, /) -> Book:
        books = self._api_call(
            method="get",
            params={"title": title},
            path="/api/v3/books/",
            response_cls=AllBooksResponse,
        )

        if not books:
            raise AppClientError(f"no books with {title=!r}")

        book = books[0]

        return book

    def update_author(
        self,
        author_id: ID,
        /,
        *,
        book_ids: Collection[ID] | None = None,
        name: str | None = None,
    ) -> Author:
        book_ids = None if book_ids is None else sorted(book_ids)
        req = UpdateAuthorRequest(book_ids=book_ids, name=name)

        author = self._api_call(
            method="patch",
            path=f"/api/v2/authors/{author_id}/",
            request=req,
            response_cls=UpdateAuthorResponse,
            statuses=(200,),
        )

        return author

    def update_book(
        self,
        book_id: ID,
        /,
        *,
        author_ids: Collection[ID] | None = None,
        title: str | None = None,
    ) -> Book:
        author_ids = None if author_ids is None else sorted(author_ids)
        req = UpdateBookRequest(author_ids=author_ids, title=title)

        book = self._api_call(
            method="patch",
            path=f"/api/v3/books/{book_id}/",
            request=req,
            response_cls=UpdateBookResponse,
            statuses=(200,),
        )

        return book

    def _api_call(
        self,
        /,
        *,
        method: str,
        params: dict | None = None,
        path: str,
        request: BaseModel | None = None,
        response_cls: Type[ApiResponse[T]],
        statuses: Collection[int] = (200,),
    ) -> T:
        content = None
        if request:
            content = request.model_dump_json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
            )

        def pretty(body: str | bytes | None) -> Any:
            if body is None:
                return body

            with suppress(orjson.JSONDecodeError):
                return orjson.loads(body)

            if isinstance(body, bytes):
                body = body.decode()

            return body

        @retry(self.config)
        def _request() -> Response:
            return self.session.request(
                content=content,
                method=method,
                params=params,
                timeout=4 + (10000 * self.config.MODE_DEBUG),
                url=path,
            )

        try:
            rs = _request()
        except tenacity.RetryError as err:
            raise AppClientError(
                f"http request failed: {err}",
                request_body=pretty(content),
                request_headers=dict(self.session.headers.items()),
                request_method=method,
                request_params=params,
                request_path=path,
            ) from err

        if rs.status_code not in statuses:
            raise AppClientError(
                "api call failed",
                request_body=pretty(rs.request.content),
                request_headers=dict(rs.request.headers.items()),
                request_method=rs.request.method,
                request_params=params,
                request_path=str(rs.request.url),
                response_body=pretty(rs.text),
                response_code=rs.status_code,
                response_headers=dict(rs.headers.items()),
            )

        payload = response_cls.model_validate_json(rs.text)
        if payload.errors:
            raise AppClientError(
                "\n".join(payload.errors),
                request_method=rs.request.method,
                request_params=params,
                request_path=str(rs.request.url),
                response_code=rs.status_code,
            )

        return cast(T, payload.data)

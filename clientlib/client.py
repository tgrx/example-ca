from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Any
from typing import Collection
from typing import Type
from typing import TypeVar
from typing import cast

import attrs
import orjson
import tenacity
from pydantic import BaseModel

from clientlib.entities import AllAuthorsResponse
from clientlib.entities import ApiResponse
from clientlib.entities import CreateAuthorRequest
from clientlib.entities import CreateAuthorResponse
from clientlib.entities import DeleteAuthorResponse
from clientlib.entities import GetAuthorResponse
from clientlib.entities import UpdateAuthorRequest
from clientlib.entities import UpdateAuthorResponse
from clientlib.errors import AppClientError

if TYPE_CHECKING:
    from uuid import UUID

    from httpx import Client
    from httpx import Response

    from app.entities.models import Author


T = TypeVar("T")


retry = tenacity.retry(
    stop=tenacity.stop_after_attempt(4),
    wait=tenacity.wait_exponential_jitter(
        exp_base=2,
        initial=1,
        jitter=1,
        max=10,
    ),
)


@attrs.frozen(kw_only=True, slots=True)
class AppClient:
    """
    The very first client of the whole app
    """

    session: "Client"

    def create_author(self, *, name: str) -> "Author":
        author = self._api_call(
            method="post",
            path="/api/v2/authors/",
            request=CreateAuthorRequest(name=name),
            response_cls=CreateAuthorResponse,
            statuses=(201,),
        )

        return author

    def delete_author_by_id(
        self,
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        return self._api_call(
            method="delete",
            path=f"/api/v2/authors/{id}/",
            response_cls=DeleteAuthorResponse,
        )

    def get_all_authors(self) -> list["Author"]:
        authors = self._api_call(
            method="get",
            path="/api/v1/authors/",
            response_cls=AllAuthorsResponse,
        )

        return authors

    def get_author_by_id(
        self,
        id: "UUID",  # noqa: A002,VNE003
    ) -> "Author":
        author = self._api_call(
            method="get",
            path=f"/api/v2/authors/{id}/",
            response_cls=GetAuthorResponse,
            statuses=(200, 404),
        )

        return author

    def get_author_by_name(
        self,
        name: str,  # noqa: A002,VNE003
    ) -> "Author":
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

    def update_author(
        self,
        *,
        id: "UUID",  # noqa: A002
        name: str,
    ) -> "Author":
        author = self._api_call(
            method="patch",
            path=f"/api/v2/authors/{id}/",
            request=UpdateAuthorRequest(name=name),
            response_cls=UpdateAuthorResponse,
            statuses=(200,),
        )

        return author

    def _api_call(
        self,
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
            content = request.model_dump_json(by_alias=True)

        def pretty(body: str | bytes | None) -> Any:
            if body is None:
                return body

            with suppress(orjson.JSONDecodeError):
                return orjson.loads(body)

            if isinstance(body, bytes):
                body = body.decode()

            return body

        @retry
        def _request() -> "Response":
            return self.session.request(
                content=content,
                method=method,
                params=params,
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

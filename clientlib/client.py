from typing import TYPE_CHECKING

import attrs
import tenacity

from clientlib.entities import AllAuthorsResponse
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

    from app.entities.models import Author


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

    @retry
    def create_author(self, *, name: str) -> "Author":
        request = CreateAuthorRequest(name=name)
        request_body = request.model_dump_json()

        response = self.session.post(
            "/api/v2/authors/",
            content=request_body,
        )

        if response.status_code != 201:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = CreateAuthorResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot create author",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        author = payload.data

        return author

    @retry
    def delete_author_by_id(
        self,
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        response = self.session.delete(f"/api/v2/authors/{id}/")

        if response.status_code != 200:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = DeleteAuthorResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot delete author",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        return payload.data

    @retry
    def get_all_authors(self) -> list["Author"]:
        response = self.session.get("/api/v1/authors/")
        if response.status_code != 200:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = AllAuthorsResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot get authors",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        authors = payload.data

        return authors

    @retry
    def get_author_by_id(
        self,
        id: "UUID",  # noqa: A002,VNE003
    ) -> "Author":
        response = self.session.get(f"/api/v2/authors/{id}/")

        if response.status_code != 200:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = GetAuthorResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot get author",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        author = payload.data

        return author

    @retry
    def get_author_by_name(
        self,
        name: str,  # noqa: A002,VNE003
    ) -> "Author":
        response = self.session.get(
            "/api/v2/authors/",
            params={
                "name": name,
            },
        )

        if response.status_code != 200:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = AllAuthorsResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot get author",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        authors = payload.data
        author = authors[0]

        return author

    @retry
    def update_author(
        self,
        *,
        id: "UUID",  # noqa: A002
        name: str,
    ) -> "Author":
        request = UpdateAuthorRequest(name=name)
        request_body = request.model_dump_json()

        response = self.session.patch(
            f"/api/v2/authors/{id}/",
            content=request_body,
        )

        if response.status_code != 200:
            raise AppClientError(
                "unsuccessful api call",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        payload = UpdateAuthorResponse.model_validate_json(response.text)
        if payload.errors:
            raise AppClientError(
                "cannot update author",
                code=response.status_code,
                headers=dict(response.headers.items()),
                payload=response.text,
            )

        author = payload.data

        return author

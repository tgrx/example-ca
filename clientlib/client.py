from typing import TYPE_CHECKING

import attrs
import tenacity

from clientlib.entities import AllAuthorsResponse
from clientlib.errors import AppClientError

if TYPE_CHECKING:
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

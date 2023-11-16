import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clientlib.client import AppClient


def test_user_can_create_and_retrieve_author(
    *,
    client: "AppClient",
) -> None:
    salt = os.urandom(4).hex()
    name = f"author {salt}"

    author_created = client.create_author(name=name)

    assert author_created.id
    assert author_created.name == name

    author_retrieved = client.get_author_by_id(id=author_created.id)

    assert author_retrieved == author_created

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clientlib.client import AppClient


def test_user_can_create_author(
    *,
    client: "AppClient",
) -> None:
    salt = os.urandom(4).hex()
    name = f"author {salt}"
    author = client.create_author(name=name)

    assert author.id
    assert author.name == name

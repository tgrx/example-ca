import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from app.entities.models import Author
    from clientlib.client import AppClient


def test_author_crud(
    *,
    client: "AppClient",
) -> None:
    salt = os.urandom(4).hex()
    name1 = f"author-{salt}-1"
    name2 = f"author-{salt}-2"

    assert_no_author(client, name2)
    assert_no_author(client, name1)

    assert_author_created(client, name1)
    author = assert_author_exists(client, name1)
    assert_no_author(client, name2)

    assert_author_updated(client, author.id, name2)
    assert_author_exists(client, name2)
    assert_no_author(client, name1)

    delete_author(client, name2)
    assert_no_author(client, name2)
    assert_no_author(client, name1)


def assert_author_created(client: "AppClient", name: str) -> "Author":
    author = client.create_author(name=name)
    assert author.id
    assert author.name == name
    return author


def assert_author_exists(client: "AppClient", name: str) -> "Author":
    author = client.get_author_by_name(name)
    author_retrieved = client.get_author_by_id(author.id)
    assert author_retrieved == author
    return author


def assert_author_updated(
    client: "AppClient",
    id: "UUID",  # noqa: A002,VNE003
    name: str,
) -> "Author":
    author = client.update_author(id, name=name)
    assert author.id == id
    assert author.name == name
    return author


def assert_no_author(client: "AppClient", name: str) -> None:
    authors = client.get_all_authors()
    authors_with_name = {
        author.id for author in authors if author.name == name
    }
    assert len(authors_with_name) == 0


def delete_author(client: "AppClient", name: str) -> None:
    author = assert_author_exists(client, name)
    client.delete_author_by_id(author.id)

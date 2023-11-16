import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.models import Author
    from clientlib.client import AppClient


def test_author_crud(
    *,
    client: "AppClient",
) -> None:
    salt = os.urandom(4).hex()
    name1 = f"author-{salt}-1"

    assert_no_author(client, name1)

    author_created = assert_author_created(client, name1)
    assert_author_exists(client, author_created)

    delete_author(client, author_created)
    assert_no_author(client, name1)


def assert_no_author(client: "AppClient", name: str) -> None:
    authors = client.get_all_authors()
    authors_with_name = {
        author.id for author in authors if author.name == name
    }
    assert len(authors_with_name) == 0


def assert_author_created(client: "AppClient", name: str) -> "Author":
    author = client.create_author(name=name)
    assert author.id
    assert author.name == name
    return author


def assert_author_exists(client: "AppClient", author: "Author") -> None:
    authors = client.get_all_authors()
    assert author in authors

    author_retrieved = client.get_author_by_id(id=author.id)
    assert author_retrieved == author


def delete_author(client: "AppClient", author: "Author") -> None:
    client.delete_author_by_id(id=author.id)

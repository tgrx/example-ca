from faker import Faker

from app.entities.models import ID
from app.entities.models import Author
from clientlib.client import AppClient


def test_author_crud(
    *,
    client: AppClient,
    faker: Faker,
) -> None:
    name1 = faker.name()
    name2 = faker.name()

    no_author(client, name2)
    no_author(client, name1)

    author_created(client, name1)
    author = author_exists(client, name1)
    no_author(client, name2)

    duplicate_forbidden(client, name1)

    author_updated(client, author.author_id, name2)
    author_exists(client, name2)
    no_author(client, name1)

    delete_author(client, name2)
    no_author(client, name2)
    no_author(client, name1)


def author_created(client: AppClient, name: str, /) -> Author:
    author = client.create_author(name=name)
    assert author.author_id
    assert author.name == name
    return author


def author_exists(client: AppClient, name: str, /) -> Author:
    author = client.get_author_by_name(name)
    author_retrieved = client.get_author_by_id(author.author_id)
    assert author_retrieved == author
    return author


def author_updated(
    client: AppClient,
    author_id: ID,
    name: str,
    /,
) -> Author:
    author = client.update_author(author_id, name=name)
    assert author.author_id == author_id
    assert author.name == name
    return author


def duplicate_forbidden(client: AppClient, name: str) -> None:
    author = client.create_author(name=name)
    assert author.author_id
    assert author.name == name


def no_author(client: AppClient, name: str, /) -> None:
    authors = client.get_all_authors()
    authors_with_name = {
        author.author_id for author in authors if author.name == name
    }
    assert len(authors_with_name) == 0


def delete_author(client: AppClient, name: str, /) -> None:
    author = author_exists(client, name)
    client.delete_author_by_id(author.author_id)

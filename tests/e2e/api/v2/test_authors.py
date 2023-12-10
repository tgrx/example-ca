from uuid import uuid4

from faker import Faker

from app.entities.models import ID
from app.entities.models import Author
from clientlib.client import AppClient
from clientlib.errors import AppClientError


def test_author_crud(
    *,
    client: AppClient,
    faker: Faker,
) -> None:
    name1 = faker.name()
    name2 = faker.name()

    lost(client, name1)
    lost(client, name2)

    created(client, name1)
    author = exists(client, name1)
    lost(client, name2)
    cannot_create_with_taken_name(client, name1)

    updated(client, author.author_id, name2)
    exists(client, name2)
    lost(client, name1)

    created(client, name1)
    author1 = exists(client, name1)
    author2 = exists(client, name2)
    cannot_create_with_taken_name(client, name1)
    cannot_create_with_taken_name(client, name2)
    cannot_update_with_taken_name(client, author1.author_id, author2.name)

    cannot_update_lost(client, faker)

    delete(client, name1)
    lost(client, name1)
    exists(client, name2)

    delete(client, name2)
    lost(client, name1)
    lost(client, name2)


def created(client: AppClient, name: str, /) -> Author:
    # todo: deal with book ids
    author = client.create_author(book_ids=[], name=name)
    assert author.author_id
    assert author.name == name
    return author


def exists(client: AppClient, name: str, /) -> Author:
    author = client.get_author_by_name(name)
    author_retrieved = client.get_author_by_id(author.author_id)
    assert author_retrieved == author
    return author


def updated(
    client: AppClient,
    author_id: ID,
    name: str,
    /,
) -> Author:
    author = client.update_author(author_id, name=name)
    assert author.author_id == author_id
    assert author.name == name
    return author


def cannot_create_with_taken_name(client: AppClient, name: str) -> None:
    try:
        # todo: deal with book ids
        client.create_author(book_ids=[], name=name)
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert error == f"author name {name!r} is already taken"


def cannot_update_with_taken_name(
    client: AppClient, author_id: ID, name: str
) -> None:
    try:
        client.update_author(author_id, name=name)
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert error == f"author name {name!r} is already taken"


def cannot_update_lost(client: AppClient, faker: Faker) -> None:
    lost_author_id = uuid4()
    name = faker.name()
    try:
        client.update_author(lost_author_id, name=name)
    except AppClientError as err:
        assert err.response_code == 404

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert error == f"no author with author_id={lost_author_id!s}"


def lost(client: AppClient, name: str, /) -> None:
    authors = client.get_all_authors()
    authors_with_name = {
        author.author_id for author in authors if author.name == name
    }
    assert len(authors_with_name) == 0


def delete(client: AppClient, name: str, /) -> None:
    author = exists(client, name)
    client.delete_author_by_id(author.author_id)

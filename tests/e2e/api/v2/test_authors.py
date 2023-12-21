from typing import Collection
from uuid import uuid4

from faker import Faker

from app.entities.models import Author
from app.entities.models import Book
from clientlib.client import AppClient
from clientlib.errors import AppClientError


def test_crud(
    client: AppClient,
    faker: Faker,
    laws: Book,
    republic: Book,
) -> None:
    plato_el = "Πλάτων"
    plato_en = "Plato"

    lost(client, plato_el)
    lost(client, plato_en)

    cannot_create_degenerate(client, plato_el)

    created(client, plato_el, [laws])
    plato = exists(client, plato_el)
    lost(client, plato_en)

    cannot_create_with_taken_name(client, plato_el)

    plato = updated(client, plato, name=plato_en)
    lost(client, plato_el)
    exists(client, plato_en)

    plato = updated(client, plato, books=[laws, republic])
    plato = updated(client, plato, books=[republic, laws])
    plato = updated(client, plato, books=[republic])

    plato = created(client, plato_el, [laws])
    exists(client, plato_el)
    exists(client, plato_en)

    cannot_create_with_taken_name(client, plato_el)
    cannot_create_with_taken_name(client, plato_en)
    cannot_make_degenerate(client, plato)
    cannot_update_lost(client, faker)
    cannot_update_with_taken_name(client, plato, plato_el)

    delete(client, plato_el)
    lost(client, plato_el)
    exists(client, plato_en)

    delete(client, plato_en)
    lost(client, plato_el)
    lost(client, plato_en)


def cannot_create_degenerate(client: AppClient, name: str, /) -> None:
    try:
        client.create_author(book_ids=[], name=name)
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert (
            error
            == f"The Author({name=!r}) will become degenerate without books."
        )


def cannot_create_with_taken_name(client: AppClient, name: str, /) -> None:
    try:
        client.create_author(book_ids=[], name=name)
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert error == f"The Author({name=!r}) already exists."


def cannot_make_degenerate(client: AppClient, author: Author, /) -> None:
    try:
        client.update_author(author.author_id, book_ids=[])
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        expected_error = (
            f"The Author(author_id={author.author_id}, name={author.name!r})"
            " will become degenerate without books."
        )
        assert error == expected_error


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
        assert (
            error == f"The Author(author_id={lost_author_id}) does not exist."
        )


def cannot_update_with_taken_name(
    client: AppClient,
    author: Author,
    name: str,
    /,
) -> None:
    try:
        client.update_author(author.author_id, name=name)
    except AppClientError as err:
        assert err.response_code == 409

        assert isinstance(err.response_body, dict)

        errors = err.response_body.get("errors")
        assert isinstance(errors, list)
        assert len(errors) == 1

        error = errors[0]
        assert error == f"author name {name!r} is already taken"


def created(
    client: AppClient,
    name: str,
    books: Collection[Book],
    /,
) -> Author:
    book_ids = [i.book_id for i in books]
    author = client.create_author(book_ids=book_ids, name=name)
    assert author.author_id  # todo: check valid uuid
    assert author.book_ids == book_ids
    assert author.name == name
    return author


def delete(client: AppClient, name: str, /) -> None:
    author = exists(client, name)
    client.delete_author_by_id(author.author_id)


def exists(client: AppClient, name: str, /) -> Author:
    found_by_name = client.get_author_by_name(name)
    assert found_by_name is not None
    found_by_id = client.get_author_by_id(found_by_name.author_id)
    assert found_by_id == found_by_name
    return found_by_id


def lost(client: AppClient, name: str, /) -> None:
    authors = client.get_all_authors()
    authors_with_name = {
        author.author_id for author in authors if author.name == name
    }
    assert len(authors_with_name) == 0


def updated(
    client: AppClient,
    original: Author,
    /,
    *,
    books: Collection[Book] | None = None,
    name: str | None = None,
) -> Author:
    book_ids = (
        None
        if books is None
        else [i.book_id for i in sorted(books, key=lambda i: i.title)]
    )
    updated = client.update_author(
        original.author_id,
        book_ids=book_ids,
        name=name,
    )

    assert updated.author_id == original.author_id

    if books is not None:
        assert updated.book_ids == book_ids
    else:
        assert updated.book_ids == original.book_ids

    if name is not None:
        assert updated.name == name
    else:
        assert updated.name == original.name

    return updated

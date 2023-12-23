from typing import Collection
from uuid import uuid4
from devtools import debug

import pytest
from faker import Faker

from app.entities.models import Author
from app.entities.models import Book
from clientlib.client import AppClient
from clientlib.errors import AppClientError


@pytest.mark.e2e
def test_crud(
    client: AppClient,
    faker: Faker,
    grimm_jacob: Author,
    grimm_wilhelm: Author,
) -> None:
    title_de = "Hänsel und Gretel"
    title_en = "Hansel and Gretel"

    lost(client, title_de)
    lost(client, title_en)

    created(client, authors=[grimm_jacob, grimm_wilhelm], title=title_de)
    book_en = exists(client, title_de)
    lost(client, title_en)

    cannot_create_with_taken_title(client, title_de)

    book_en = updated(client, book_en, title=title_en)
    lost(client, title_de)
    exists(client, title_en)

    book_en = updated(client, book_en, authors=[grimm_jacob])
    book_en = updated(client, book_en, authors=[grimm_jacob, grimm_wilhelm])
    book_en = updated(client, book_en, authors=[grimm_wilhelm])
    book_en = updated(client, book_en, authors=[grimm_wilhelm, grimm_jacob])

    cannot_update_lost(client, faker)

    created(client, title=title_de)
    exists(client, title_de)
    exists(client, title_en)

    delete(client, title_de)
    lost(client, title_de)
    exists(client, title_en)

    delete(client, title_en)
    lost(client, title_de)
    lost(client, title_en)

    cannot_make_degenerates(client, [grimm_jacob, grimm_wilhelm])


def cannot_make_degenerates(
    client: AppClient,
    authors: Collection[Author],
    /,
) -> None:
    authors_i = iter(authors)
    books_in_common = set(next(authors_i).book_ids)
    for author in authors_i:
        books_in_common &= set(author.book_ids)
    assert books_in_common
    book_in_common = books_in_common.pop()
    with pytest.raises(AppClientError) as excinfo:
        client.delete_book_by_id(book_in_common)

    exc = excinfo.value
    assert exc.response_code == 409

    assert isinstance(exc.response_body, dict)

    errors = exc.response_body.get("errors")
    assert isinstance(errors, list)
    assert len(errors) == 2

    expected = [
        f"The Author(author_id={author.author_id}, name={author.name!r})"
        " will become degenerate without books."
        for author in sorted(authors, key=lambda i: i.name)
    ]
    assert errors == expected


def cannot_create_with_taken_title(
    client: AppClient,
    title: str,
    /,
) -> None:
    with pytest.raises(AppClientError) as excinfo:
        client.create_book(title=title)

    err = excinfo.value

    assert err.response_code == 409
    assert isinstance(err.response_body, dict)
    errors = err.response_body.get("errors")
    assert isinstance(errors, list)
    assert len(errors) == 1
    error = errors[0]
    expected = f"The Book({title=!r}) already exists."
    assert error == expected


def cannot_update_lost(
    client: AppClient,
    faker: Faker,
    /,
) -> None:
    lost_id = uuid4()
    lost_title = faker.name()
    with pytest.raises(AppClientError) as excinfo:
        client.update_book(lost_id, title=lost_title)

    err = excinfo.value

    assert err.response_code == 404
    assert isinstance(err.response_body, dict)
    errors = err.response_body.get("errors")
    assert isinstance(errors, list)
    assert len(errors) == 1
    error = errors[0]
    expected = f"The Book(book_id={lost_id}) does not exist."
    assert error == expected


def created(
    client: AppClient,
    /,
    *,
    title: str,
    authors: Collection[Author] | None = None,
) -> Book:
    author_ids = None
    if authors:
        author_ids = [i.author_id for i in authors]
    book = client.create_book(author_ids=author_ids, title=title)
    debug(XXX_book=book, XXX_authors=authors)

    assert book.book_id
    assert book.title == title

    compare_to = [] if author_ids is None else author_ids
    assert book.author_ids == compare_to

    return book


def exists(client: AppClient, title: str, /) -> Book:
    book = client.get_book_by_title(title)
    book_by_id = client.get_book_by_id(book.book_id)

    assert book_by_id == book
    assert book.title == title

    return book


def updated(
    client: AppClient,
    book_original: Book,
    /,
    *,
    authors: list[Author] | None = None,
    title: str | None = None,
) -> Book:
    author_ids = None
    if authors is not None:
        author_ids = [
            i.author_id for i in sorted(authors, key=lambda i: i.name)
        ]

    book_updated = client.update_book(
        book_original.book_id,
        author_ids=author_ids,
        title=title,
    )

    assert book_original.book_id == book_updated.book_id

    if title is not None and title != book_original.title:
        assert book_updated.title != book_original.title
        assert book_updated.title == title
    else:
        assert book_updated.title == book_original.title
        assert book_updated.title != title

    if authors is not None and author_ids != book_original.author_ids:
        assert book_updated.author_ids != book_original.author_ids
        assert book_updated.author_ids == author_ids
    else:
        assert book_updated.author_ids == book_original.author_ids
        assert book_updated.author_ids != author_ids

    return book_updated


def lost(client: AppClient, title: str, /) -> None:
    with pytest.raises(AppClientError):
        client.get_book_by_title(title)


def delete(client: AppClient, title: str, /) -> None:
    book = exists(client, title)
    client.delete_book_by_id(book.book_id)

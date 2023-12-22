from faker import Faker
import pytest

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from clientlib.client import AppClient


@pytest.mark.e2e
def test_book_crud(
    client: AppClient,
    faker: Faker,
    grimm_jacob: Author,
    grimm_wilhelm: Author,
) -> None:
    title_de = "Hänsel und Gretel"
    title_en = "Hansel and Gretel"

    lost(client, title_de)
    lost(client, title_en)

    created(client, title_de, [grimm_jacob, grimm_wilhelm])
    book_en = exists(client, title_de)
    lost(client, title_en)

    cannot_create_with_taken_title(client, title_de)

    book_en = updated(client, book_en, title=title_en)
    lost(client, title_de)
    exists(client, title_en)

    book_en = updated(client, book_en, authors=[grimm_jacob, grimm_jacob])
    book_en = updated(client, book_en, authors=[grimm_jacob, grimm_wilhelm])
    book_en = updated(client, book_en, authors=[grimm_jacob])
    book_en = updated(client, book_en, authors=[grimm_wilhelm, grimm_jacob])
    book_en = updated(client, book_en, authors=[grimm_wilhelm])

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


def book_created(
    client: AppClient,
    title: str,
    authors: list[Author],
    /,
) -> Book:
    author_ids = [author.author_id for author in authors]
    assert author_ids  # todo: deal with it
    book = client.create_book(title=title)

    assert book.book_id
    assert book.title == title
    assert book.author_ids == authors

    return book


def book_exists(
    client: AppClient,
    /,
    *,
    authors: list[Author] | None = None,
    title: str,
) -> Book:
    book = client.get_book_by_title(title)
    book_by_id = client.get_book_by_id(book.book_id)

    assert book_by_id == book

    if authors is not None:
        assert book.author_ids == authors

    assert book.title == title

    return book


def book_updated(
    client: AppClient,
    book_id: ID,
    /,
    *,
    authors: list[Author] | None = None,
    title: str | None = None,
) -> Book:
    book_original = client.get_book_by_id(book_id)
    author_ids = None
    if authors is not None:
        author_ids = [author.author_id for author in authors]
    book_updated = client.update_book(
        book_id,
        author_ids=author_ids,
        title=title,
    )

    assert book_original.book_id == book_updated.book_id

    if title is not None and title != book_original.title:
        assert book_original.title != book_updated.title
        assert book_updated.title == title
    else:
        assert book_original.title == book_updated.title
        assert book_updated.title != title

    if authors is not None and authors != book_original.author_ids:
        assert book_original.author_ids != book_updated.author_ids
        assert book_updated.author_ids == authors
    else:
        assert book_original.author_ids == book_updated.author_ids
        assert book_updated.author_ids != authors

    return book_updated


def no_book(client: AppClient, title: str, /) -> None:
    books = client.get_all_books()
    books_with_title = {book.book_id for book in books if book.title == title}
    assert len(books_with_title) == 0


def delete_book(client: AppClient, title: str, /) -> None:
    book = book_exists(client, title=title)
    client.delete_book_by_id(book.book_id)

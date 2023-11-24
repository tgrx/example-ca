from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book
from clientlib.client import AppClient


def test_book_crud(
    *,
    client: AppClient,
    installed_authors: dict[ID, Author],
) -> None:
    pushkin = next(
        filter(lambda a: "Pushkin" in a.name, installed_authors.values())
    )
    pelevin = next(
        filter(lambda a: "Pelevin" in a.name, installed_authors.values())
    )

    title_pushkin = f"Biography of {pushkin.name}"
    title_pelevin = f"Biography of {pelevin.name}"

    assert_no_book(client, title_pushkin)
    assert_no_book(client, title_pelevin)

    assert_book_created(client, title_pushkin, [pushkin])
    book = assert_book_exists(client, authors=[pushkin], title=title_pushkin)
    assert_no_book(client, title_pelevin)

    assert_book_updated(
        client,
        book.book_id,
        authors=[pushkin, pelevin],
        title=title_pelevin,
    )
    assert_book_exists(client, authors=[pushkin, pelevin], title=title_pelevin)
    assert_no_book(client, title_pushkin)

    assert_book_updated(client, book.book_id, authors=[pushkin])
    assert_book_exists(client, authors=[pushkin], title=title_pelevin)

    assert_book_updated(client, book.book_id, authors=[pelevin])
    assert_book_exists(client, authors=[pelevin], title=title_pelevin)

    assert_book_updated(client, book.book_id, authors=[])
    assert_book_exists(client, authors=[], title=title_pelevin)

    delete_book(client, title_pelevin)
    assert_no_book(client, title_pelevin)
    assert_no_book(client, title_pushkin)


def assert_book_created(
    client: AppClient,
    title: str,
    authors: list[Author],
    /,
) -> Book:
    author_ids = [author.author_id for author in authors]
    book = client.create_book(author_ids=author_ids, title=title)

    assert book.book_id
    assert book.title == title
    assert book.authors == authors

    return book


def assert_book_exists(
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
        assert book.authors == authors

    assert book.title == title

    return book


def assert_book_updated(
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
        book_id, author_ids=author_ids, title=title
    )

    assert book_original.book_id == book_updated.book_id

    if title is not None and title != book_original.title:
        assert book_original.title != book_updated.title
        assert book_updated.title == title
    else:
        assert book_original.title == book_updated.title
        assert book_updated.title != title

    if authors is not None and authors != book_original.authors:
        assert book_original.authors != book_updated.authors
        assert book_updated.authors == authors
    else:
        assert book_original.authors == book_updated.authors
        assert book_updated.authors != authors

    return book_updated


def assert_no_book(client: AppClient, title: str, /) -> None:
    books = client.get_all_books()
    books_with_title = {book.book_id for book in books if book.title == title}
    assert len(books_with_title) == 0


def delete_book(client: AppClient, title: str, /) -> None:
    book = assert_book_exists(client, title=title)
    client.delete_book_by_id(book.book_id)

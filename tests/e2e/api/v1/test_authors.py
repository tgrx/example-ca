from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from app.entities.models import Author
    from clientlib.client import AppClient


def test_can_get_all_authors_empty(
    *,
    client: "AppClient",
) -> None:
    authors = client.get_all_authors()

    assert authors == []


def test_can_get_all_authors_installed(
    *,
    client: "AppClient",
    installed_authors: dict["UUID", "Author"],
) -> None:
    authors = client.get_all_authors()

    assert len(authors) == len(installed_authors)

    for requested in authors:
        installed = installed_authors.get(requested.id)
        assert installed, f"no author with id={requested.id} is installed"
        assert requested == installed


def test_can_get_all_authors_with_books_installed(
    *,
    client: "AppClient",
    installed_authors_with_books: dict["UUID", "Author"],
) -> None:
    authors = client.get_all_authors()

    assert len(authors) == len(installed_authors_with_books)

    for requested in authors:
        installed = installed_authors_with_books.get(requested.id)
        assert installed, f"no author with id={requested.id} is installed"
        assert requested == installed

from app.entities.models import ID
from app.entities.models import Author
from clientlib.client import AppClient


def test_can_get_all_authors_empty(*, client: AppClient) -> None:
    authors = client.get_all_authors()

    assert authors == []


def test_can_get_all_authors_installed(
    *,
    client: AppClient,
    installed_authors: dict[ID, Author],
) -> None:
    authors = client.get_all_authors()

    assert len(authors) == len(installed_authors)

    for requested in authors:
        installed = installed_authors.get(requested.author_id)

        _err = f"no author with author_id={requested.author_id} is installed"
        assert installed, _err

        assert requested == installed


def test_can_get_all_authors_with_books_installed(
    *,
    client: AppClient,
    installed_authors_with_books: dict[ID, Author],
) -> None:
    authors = client.get_all_authors()

    assert len(authors) == len(installed_authors_with_books)

    for requested in authors:
        installed = installed_authors_with_books.get(requested.author_id)

        _err = f"no author with id={requested.author_id} is installed"
        assert installed, _err

        assert requested == installed

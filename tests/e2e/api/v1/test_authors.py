from app.entities.models import Author
from clientlib.client import AppClient


def test_can_get_all_authors_empty(*, client: AppClient) -> None:
    authors = client.get_all_authors()

    assert authors == []


def test_can_get_all_authors_installed(
    *,
    client: AppClient,
    james_joyce: Author,
    victor_pelevin: Author,
) -> None:
    authors = client.get_all_authors()

    assert authors == [james_joyce, victor_pelevin]

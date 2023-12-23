import pytest

from app.entities.models import Author
from app.usecases.author import FindAuthorsUseCase


@pytest.mark.unit
def test_find_all(
    find_authors: FindAuthorsUseCase,
    grimm_jacob: Author,
    grimm_wilhelm: Author,
) -> None:
    authors = find_authors()
    assert authors == [grimm_jacob, grimm_wilhelm]


@pytest.mark.unit
def test_find_by_name(
    find_authors: FindAuthorsUseCase,
    grimm_jacob: Author,
    grimm_wilhelm: Author,
) -> None:
    for author in [grimm_jacob, grimm_wilhelm]:
        found = find_authors(name=author.name)
        assert found == [author]


@pytest.mark.unit
def test_find_by_pk(
    find_authors: FindAuthorsUseCase,
    grimm_jacob: Author,
    grimm_wilhelm: Author,
) -> None:
    for author in [grimm_jacob, grimm_wilhelm]:
        found = find_authors(author_id=author.author_id)
        assert found == [author]


__all__ = (
    "test_find_all",
    "test_find_by_name",
    "test_find_by_pk",
)

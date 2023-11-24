from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import FindAuthorsUseCase


def test_usecase_no_filter(
    *,
    author_repo: AuthorRepo,
    find_authors: FindAuthorsUseCase,
    installed_authors: list[Author],
) -> None:
    authors = find_authors()

    assert authors == installed_authors
    assert authors == author_repo.get_all()


def test_usecase_filter_by_pk(
    *,
    find_authors: FindAuthorsUseCase,
    installed_authors: list[Author],
) -> None:
    installed_author = installed_authors[-1]
    authors = find_authors(author_id=installed_author.author_id)

    assert len(authors) == 1
    author = authors[0]

    assert author == installed_author
    assert author.name == "author d"


def test_usecase_filter_by_name(
    *,
    find_authors: FindAuthorsUseCase,
    installed_authors: list[Author],
) -> None:
    authors = find_authors(name="author b")

    assert len(authors) == 1
    author = authors[0]

    assert author in installed_authors
    assert author.name == "author b"

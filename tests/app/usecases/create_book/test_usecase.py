from app.entities.interfaces import BookRepo
from app.entities.models import Author
from app.usecases.book import CreateBookUseCase


def test_usecase(
    *,
    author: Author,
    book_repo: BookRepo,
    create_book: CreateBookUseCase,
) -> None:
    title = f"Bio of {author.name}"
    assert book_repo.get_by_title(title) is None

    book = create_book(title=title, author_ids=[author.author_id])

    book_in_repo = book_repo.get_by_title(title)
    assert book_in_repo == book

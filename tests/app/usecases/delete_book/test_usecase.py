from app.entities.interfaces import BookRepo
from app.entities.models import Book
from app.usecases.book import DeleteBookUseCase


def test_usecase(
    *,
    book_repo: BookRepo,
    delete_book: DeleteBookUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    assert book_repo.get_by_id(finnegans_wake.book_id) == finnegans_wake
    assert book_repo.get_by_id(ulysses.book_id) == ulysses

    delete_book(finnegans_wake.book_id)

    assert book_repo.get_by_id(finnegans_wake.book_id) is None
    assert book_repo.get_by_id(ulysses.book_id) == ulysses

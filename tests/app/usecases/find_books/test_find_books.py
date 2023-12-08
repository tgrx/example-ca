from app.entities.models import Book
from app.usecases.book import FindBooksUseCase


def test_find_all(
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    books = find_books()
    assert books == [finnegans_wake, ulysses]


def test_find_by_pk(
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    for book in {finnegans_wake, ulysses}:
        found = find_books(book_id=book.book_id)
        assert found == [book]


def test_find_by_title(
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    for book in {finnegans_wake, ulysses}:
        found = find_books(title=book.title)
        assert found == [book]


__all__ = (
    "test_find_all",
    "test_find_by_pk",
    "test_find_by_title",
)

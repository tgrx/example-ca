from app.entities.interfaces import BookRepo
from app.entities.models import Book
from app.usecases.book import FindBooksUseCase


def test_usecase_no_filter(
    *,
    book_repo: BookRepo,
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    books = find_books()

    assert books == [finnegans_wake, ulysses]
    assert books == book_repo.get_all()


def test_usecase_filter_by_pk(
    *,
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    for book in (finnegans_wake, ulysses):
        found = find_books(book_id=book.book_id)
        assert found == [book]


def test_usecase_filter_by_title(
    *,
    find_books: FindBooksUseCase,
    finnegans_wake: Book,
    ulysses: Book,
) -> None:
    for book in (finnegans_wake, ulysses):
        found = find_books(title=book.title)
        assert found == [book]

from app.entities.models import Author
from app.entities.models import Book
from app.usecases.book import UpdateBookUseCase


def test_usecase_full_update(
    *,
    ulysses: Book,
    update_book: UpdateBookUseCase,
    victor_pelevin: Author,
) -> None:
    snuff = update_book(
        ulysses.book_id,
        author_ids=[victor_pelevin.author_id],
        title="S.N.U.F.F.",
    )
    assert snuff.book_id == ulysses.book_id

    assert snuff.authors == [victor_pelevin]
    assert snuff.title == "S.N.U.F.F."


def test_usecase_update_authors(
    *,
    james_joyce: Author,
    ulysses: Book,
    update_book: UpdateBookUseCase,
    victor_pelevin: Author,
) -> None:
    updated = update_book(
        ulysses.book_id,
        author_ids=[victor_pelevin.author_id, james_joyce.author_id],
    )
    assert updated.authors != ulysses.authors
    assert updated.authors == [james_joyce, victor_pelevin]
    assert updated.book_id == ulysses.book_id
    assert updated.title == ulysses.title

    updated2 = update_book(updated.book_id, author_ids=[james_joyce.author_id])
    assert updated2 == ulysses
    assert updated2.authors != updated.authors
    assert updated2.book_id == updated.book_id
    assert updated2.title == updated.title

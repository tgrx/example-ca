from app.entities.interfaces import AuthorRepo
from app.entities.models import Author
from app.usecases.author import DeleteAuthorUseCase


def test_usecase(
    *,
    author_repo: AuthorRepo,
    delete_author: DeleteAuthorUseCase,
    installed_authors: dict[str, Author],
) -> None:
    pelevin = installed_authors["pelevin"]
    pushkin = installed_authors["pushkin"]

    delete_author(pelevin.author_id)

    assert author_repo.get_by_id(pelevin.author_id) is None
    assert author_repo.get_by_id(pushkin.author_id) == pushkin

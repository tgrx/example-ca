from typing import Any
from typing import Final
from typing import final

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.entities.errors import DegenerateAuthorsError
from app.entities.errors import DuplicateBookTitleError
from app.entities.errors import LostAuthorsError
from app.entities.errors import LostBooksError
from app.entities.models import to_uuid
from app.repos.django.book import BookRepo
from app.usecases.book import CreateBookUseCase
from app.usecases.book import DeleteBookUseCase
from app.usecases.book import FindBooksUseCase
from app.usecases.book import UpdateBookUseCase


@final
class BookViewSet(ViewSet):
    repo: Final = BookRepo()

    create_book: Final = CreateBookUseCase(repo=repo)
    delete_book: Final = DeleteBookUseCase(repo=repo)
    find_books: Final = FindBooksUseCase(repo=repo)
    update_book: Final = UpdateBookUseCase(repo=repo)

    def create(self, request: Request) -> Response:
        try:
            book = self.create_book(title=request.data["title"])
            if author_ids := request.data.get("author_ids"):
                author_ids = [to_uuid(i) for i in author_ids]
                book = self.update_book(book.book_id, author_ids=author_ids)
            data = book.model_dump()
            response = Response({"data": data}, status=201)
        except (DegenerateAuthorsError, DuplicateBookTitleError) as exc:
            response = Response({"errors": exc.errors}, status=409)
        except (
            LostAuthorsError,
            LostBooksError,
        ) as exc:
            response = Response({"errors": exc.errors}, status=404)

        return response

    def destroy(self, request: Request, pk: str) -> Response:
        try:
            book_id = to_uuid(pk)
            self.delete_book(book_id)
            response = Response({"data": None})
        except DegenerateAuthorsError as exc:
            response = Response({"errors": exc.errors}, status=409)

        return response

    def list(self, request: Request) -> Response:  # noqa: A003
        title = request.query_params.get("title")
        books = self.find_books(title=title)
        data = [book.model_dump() for book in books]
        response = Response({"data": data}, status=200)

        return response

    def partial_update(self, request: Request, pk: str) -> Response:
        try:
            book_id = to_uuid(pk)
            author_ids = request.data.get("author_ids")
            if author_ids is not None:
                author_ids = [to_uuid(i) for i in author_ids]
            book = self.update_book(
                book_id,
                author_ids=author_ids,
                title=request.data.get("title"),
            )
            data = book.model_dump()
            response = Response({"data": data}, status=200)
        except (DegenerateAuthorsError, DuplicateBookTitleError) as exc:
            response = Response({"errors": exc.errors}, status=409)
        except (
            LostAuthorsError,
            LostBooksError,
        ) as exc:
            response = Response({"errors": exc.errors}, status=404)

        return response

    def retrieve(self, request: Request, pk: str) -> Response:
        payload: Final[dict[str, Any]] = {}
        status = 500

        book_id = to_uuid(pk)
        books = self.find_books(book_id=book_id)
        if not books:
            payload["errors"] = [f"book with id={pk} not found"]
            status = 404
        else:
            book = books[0]
            payload["data"] = book.model_dump()
            status = 200

        response = Response(payload, status=status)

        return response

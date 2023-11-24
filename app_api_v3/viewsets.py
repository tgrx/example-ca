from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.entities.models import to_uuid
from app.repos.django.book import BookRepo
from app.usecases.book import CreateBookUseCase
from app.usecases.book import DeleteBookUseCase
from app.usecases.book import FindBooksUseCase
from app.usecases.book import UpdateBookUseCase


class BookViewSet(ViewSet):
    repo = BookRepo()

    create_book = CreateBookUseCase(repo=repo)
    delete_book = DeleteBookUseCase(repo=repo)
    find_books = FindBooksUseCase(repo=repo)
    update_book = UpdateBookUseCase(repo=repo)

    def create(self, request: Request) -> Response:
        book = self.create_book(
            author_ids=request.data["authors"],
            title=request.data["title"],
        )
        data = book.model_dump()
        response = Response({"data": data}, status=201)

        return response

    def destroy(self, request: Request, pk: str) -> Response:
        book_id = to_uuid(pk)
        self.delete_book(book_id)
        response = Response({"data": None})

        return response

    def list(self, request: Request) -> Response:  # noqa: A003
        title = request.query_params.get("title")
        books = self.find_books(title=title)
        data = [book.model_dump() for book in books]
        response = Response({"data": data}, status=200)

        return response

    def partial_update(self, request: Request, pk: str) -> Response:
        book_id = to_uuid(pk)
        book = self.update_book(
            book_id,
            author_ids=request.data.get("authors"),
            title=request.data.get("title"),
        )
        data = book.model_dump()
        response = Response({"data": data}, status=200)

        return response

    def retrieve(self, request: Request, pk: str) -> Response:
        payload: dict[str, Any] = {}
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

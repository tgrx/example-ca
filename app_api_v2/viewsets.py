from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.entities.models import to_uuid
from app.repos.django.author import AuthorRepo
from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import DeleteAuthorUseCase
from app.usecases.author import FindAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase


class AuthorViewSet(ViewSet):
    repo = AuthorRepo()

    create_author = CreateAuthorUseCase(repo=repo)
    delete_author = DeleteAuthorUseCase(repo=repo)
    find_authors = FindAuthorsUseCase(repo=repo)
    update_author = UpdateAuthorUseCase(repo=repo)

    def create(self, request: Request) -> Response:
        author = self.create_author(name=request.data["name"])
        data = author.model_dump()
        response = Response({"data": data}, status=201)

        return response

    def destroy(self, request: Request, pk: str) -> Response:
        author_id = to_uuid(pk)
        self.delete_author(author_id)
        response = Response({"data": None})

        return response

    def list(self, request: Request) -> Response:  # noqa: A003
        name = request.query_params.get("name")
        authors = self.find_authors(name=name)
        data = [author.model_dump() for author in authors]
        response = Response({"data": data}, status=200)

        return response

    def partial_update(self, request: Request, pk: str) -> Response:
        author_id = to_uuid(pk)
        author = self.update_author(author_id, name=request.data["name"])
        data = author.model_dump()
        response = Response({"data": data}, status=200)

        return response

    def retrieve(self, request: Request, pk: str) -> Response:
        payload: dict[str, Any] = {}
        status = 500

        author_id = to_uuid(pk)
        authors = self.find_authors(author_id=author_id)
        if not authors:
            payload["errors"] = [f"author with id={author_id} not found"]
            status = 404
        else:
            author = authors[0]
            payload["data"] = author.model_dump()
            status = 200

        response = Response(payload, status=status)

        return response

from typing import TYPE_CHECKING
from uuid import UUID

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.repos.django.author import AuthorRepo
from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import FindAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase
from app_api_v1.models import Author

if TYPE_CHECKING:
    from typing import Any

    from rest_framework.request import Request


class AuthorViewSet(ViewSet):
    def create(self, request: "Request") -> "Response":
        repo = AuthorRepo(model=Author)
        create_author = CreateAuthorUseCase(repo=repo)

        author = create_author(name=request.data["name"])
        data = author.model_dump()

        response = Response(
            {
                "data": data,
            },
            status=201,
        )

        return response

    def destroy(self, request: "Request", pk: str) -> "Response":
        repo = AuthorRepo(model=Author)
        repo.delete(id=UUID(pk))

        response = Response(
            {
                "data": None,
            },
        )

        return response

    def list(self, request: "Request") -> "Response":  # noqa: A003
        name = request.query_params.get("name")
        id = request.query_params.get("id")  # noqa: A001,VNE003

        repo = AuthorRepo(model=Author)
        find_authors = FindAuthorsUseCase(repo=repo)

        authors = find_authors(id=UUID(id) if id else None, name=name)
        data = [author.model_dump() for author in authors]

        response = Response(
            {
                "data": data,
            },
            status=200,
        )

        return response

    def partial_update(self, request: "Request", pk: str) -> "Response":
        repo = AuthorRepo(model=Author)
        update_author = UpdateAuthorUseCase(repo=repo)

        author = update_author(id=UUID(pk), name=request.data["name"])
        data = author.model_dump()

        response = Response(
            {
                "data": data,
            },
            status=200,
        )

        return response

    def retrieve(self, request: "Request", pk: str) -> "Response":
        repo = AuthorRepo(model=Author)
        find_authors = FindAuthorsUseCase(repo=repo)

        payload: dict[str, "Any"] = {}
        status = 500

        authors = find_authors(id=UUID(pk))
        if not authors:
            payload["errors"] = ["author with id={pk} not found"]
            status = 404
        else:
            author = authors[0]
            payload["data"] = author.model_dump()
            status = 200

        response = Response(
            payload,
            status=status,
        )

        return response

from typing import TYPE_CHECKING
from uuid import UUID

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.repos.django.author import AuthorRepo
from app.usecases.author import CreateAuthorUseCase
from app.usecases.author import GetAllAuthorsUseCase
from app.usecases.author import UpdateAuthorUseCase
from app_api_v1.models import Author

if TYPE_CHECKING:
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
        get_all_authors = GetAllAuthorsUseCase(repo=repo)

        authors = get_all_authors()
        author = next(author for author in authors if author.id == UUID(pk))
        data = author.model_dump()

        response = Response(
            {
                "data": data,
            },
            status=200,
        )

        return response

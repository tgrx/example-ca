from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.repos.django.author import AuthorRepo
from app.usecases.author import GetAllAuthorsUseCase
from app_api_v1.models import Author

if TYPE_CHECKING:
    from rest_framework.request import Request


class AuthorViewSet(ViewSet):
    def list(self, request: "Request") -> "Response":  # noqa: A003
        repo = AuthorRepo(model=Author)
        get_all_authors = GetAllAuthorsUseCase(repo=repo)

        authors = get_all_authors()

        data = [author.model_dump() for author in authors]

        response = Response(
            {
                "data": data,
            }
        )

        return response

from typing import Final
from typing import final

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.usecases.author import FindAuthorsUseCase
from app.xxx import xxx_author_repo


@final
class AuthorViewSet(ViewSet):
    # repo: Final = AuthorRepo()
    repo: Final = xxx_author_repo

    find_authors: Final = FindAuthorsUseCase(repo=repo)

    def list(self, request: Request) -> Response:  # noqa: A003
        authors = self.find_authors()
        data = [author.model_dump() for author in authors]
        response = Response({"data": data})

        return response

from typing import TYPE_CHECKING
from uuid import uuid4

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.entities.models import Author

if TYPE_CHECKING:
    from rest_framework.request import Request


class AuthorViewSet(ViewSet):
    def create(self, request: "Request") -> "Response":
        author = Author(id=uuid4(), name=request.data["name"])
        data = author.model_dump()

        response = Response(
            {
                "data": data,
            },
            status=201,
        )

        return response
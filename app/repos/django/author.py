from typing import TYPE_CHECKING
from typing import Type
from uuid import uuid4

import attrs

from app.entities.models import Author

if TYPE_CHECKING:
    from uuid import UUID

    from app_api_v1.models import Author as AuthorDjangoModel


@attrs.frozen(kw_only=True, slots=True)
class AuthorRepo:
    model: Type["AuthorDjangoModel"]  # to untangle from non-django code

    def create(
        self,
        *,
        name: str,
    ) -> "Author":
        record = self.model(
            id=uuid4(),
            name=name,
        )

        # todo: what if obj already exist, or another integrity error?
        # todo: what if db is down?
        record.save()

        author = Author.model_validate(record)

        return author

    def delete(
        self,
        *,
        id: "UUID",  # noqa: A002
    ) -> None:
        try:
            record = self.model.objects.get(id=id)
            # todo: what if integrity error?
            # todo: what if db is down?
            record.delete()
        except self.model.DoesNotExist:
            pass

    def get_all(self) -> list["Author"]:
        records = self.model.objects.all()
        authors = [Author.model_validate(record) for record in records]
        return authors


__all__ = ("AuthorRepo",)

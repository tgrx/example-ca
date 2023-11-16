from typing import Any
from typing import cast
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def repo() -> "AuthorRepo":
    storage: dict[str, Any] = {
        "id": uuid4(),
    }

    def mocked_create(name: str) -> "Author":
        storage["name"] = name
        author = Author.model_validate(storage)
        return author

    def mocked_get_all() -> list["Author"]:
        author = Author.model_validate(storage)
        return [author]

    mocked_repo = MagicMock(
        create=MagicMock(side_effect=mocked_create),
        get_all=MagicMock(side_effect=mocked_get_all),
        spec=AuthorRepo,
    )

    return cast(AuthorRepo, mocked_repo)

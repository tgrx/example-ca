from typing import cast
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.entities.interfaces import AuthorRepo
from app.entities.models import Author


@pytest.fixture(scope="function")
def repo(
    *,
    authors: list["Author"],
) -> "AuthorRepo":
    mocked_repo = MagicMock(
        get_all=MagicMock(return_value=authors),
        spec=AuthorRepo,
    )

    return cast(AuthorRepo, mocked_repo)


@pytest.fixture(scope="function")
def authors() -> list["Author"]:
    dataset = [
        Author(
            id=uuid4(),
            name="test author 1",
        ),
        Author(
            id=uuid4(),
            name="test author 2",
        ),
    ]

    return dataset

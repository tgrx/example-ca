import abc
from functools import cached_property
from typing import Collection
from typing import Mapping

import attrs

from app.entities.models import ID
from app.entities.models import Author
from app.entities.models import Book


class AppError(Exception, abc.ABC):
    @abc.abstractproperty
    def errors(self) -> list[str]:
        raise NotImplementedError


@attrs.define(kw_only=True)
class DegenerateAuthorsError(AppError):
    authors: Mapping[str, ID | None]

    @cached_property
    def errors(self) -> list[str]:
        errors = []
        for name, author_id in self.authors.items():
            author_id_str = f"{author_id=!s}" if author_id else ""
            name_str = f"{name=!r}"
            args = {author_id_str, name_str}
            args_str = ", ".join(filter(bool, sorted(args)))
            author = f"{Author.__name__}({args_str})"
            error = f"The {author} will become degenerate without books."
            errors.append(error)

        return errors


@attrs.define(kw_only=True)
class DuplicateAuthorNameError(AppError):
    name: str

    @cached_property
    def errors(self) -> list[str]:
        author = f"{Author.__name__}(name={self.name!r})"
        error = f"The {author} already exists."

        return [error]


@attrs.define(kw_only=True)
class DuplicateBookTitleError(AppError):
    title: str

    @cached_property
    def errors(self) -> list[str]:
        book = f"{Book.__name__}(title={self.title!r})"
        error = f"The {book} already exists."

        return [error]


@attrs.define(kw_only=True)
class LostAuthorsError(AppError):
    author_ids: Collection[ID]

    @cached_property
    def errors(self) -> list[str]:
        def _build_message(author_id: ID) -> str:
            text_author_id = f"{author_id=}"
            args = [text_author_id]
            text_args = ", ".join(sorted(filter(bool, args)))
            text_author = f"{Author.__name__}({text_args})"
            message = f"The {text_author} does not exist."
            return message

        messages = sorted(map(_build_message, self.author_ids))
        return messages


@attrs.define(kw_only=True)
class LostBooksError(AppError):
    book_ids: Collection[ID]

    @cached_property
    def errors(self) -> list[str]:
        def _build_message(book_id: ID) -> str:
            text_book_id = f"{book_id=}"
            args = [text_book_id]
            text_args = ", ".join(sorted(filter(bool, args)))
            text_book = f"{Book.__name__}({text_args})"
            message = f"The {text_book} does not exist."
            return message

        messages = sorted(map(_build_message, self.book_ids))
        return messages


__all__ = (
    "DegenerateAuthorsError",
    "DuplicateAuthorNameError",
    "DuplicateBookTitleError",
    "LostAuthorsError",
    "LostBooksError",
)

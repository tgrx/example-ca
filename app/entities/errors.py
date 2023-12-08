import abc
from functools import cached_property
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
class LostAuthorError(AppError):
    author_id: ID | None = None
    name: str | None = None

    @cached_property
    def errors(self) -> list[str]:
        attrs = ("author_id", "name")
        attrs_map = {a: getattr(self, a) for a in attrs}
        args = ", ".join(f"{a}={v!r}" for a, v in sorted(attrs_map.items()))
        author = f"{Author.__name__}({args})"
        message = f"The {author} does not exist."

        return [message]


@attrs.define(kw_only=True)
class LostBookError(AppError):
    book_id: ID | None = None
    title: str | None = None

    @cached_property
    def errors(self) -> list[str]:
        attrs = ("book_id", "title")
        attrs_map = {a: getattr(self, a) for a in attrs}
        args = ", ".join(f"{a}={v!r}" for a, v in sorted(attrs_map.items()))
        book = f"{Book.__name__}({args})"
        message = f"The {book} does not exist."

        return [message]


__all__ = (
    "DegenerateAuthorsError",
    "DuplicateAuthorNameError",
    "DuplicateBookTitleError",
    "LostAuthorError",
    "LostBookError",
)

import abc
from functools import cached_property

import attrs

from app.entities.models import ID


class AppError(Exception, abc.ABC):
    @abc.abstractproperty
    def errors(self) -> list[str]:
        raise NotImplementedError


@attrs.define(kw_only=True)
class DuplicateAuthorNameError(AppError):
    name: str

    @cached_property
    def errors(self) -> list[str]:
        error = f"author name {self.name!r} is already taken"
        return [error]


@attrs.define(kw_only=True)
class LostAuthorError(AppError):
    author_id: ID | None = None
    name: str | None = None

    @cached_property
    def errors(self) -> list[str]:
        errors = []
        if self.author_id:
            errors.append(f"no author with author_id={self.author_id!s}")
        if self.name:
            errors.append(f"no author with name={self.name!r}")
        return sorted(errors)


__all__ = (
    "DuplicateAuthorNameError",
    "LostAuthorError",
)

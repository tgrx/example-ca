class AppError(Exception):
    pass


class AuthorAlreadyExistError(AppError):
    pass


__all__ = ("AuthorAlreadyExistError",)

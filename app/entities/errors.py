class AppError(Exception):
    pass


class DuplicateAuthorError(AppError):
    pass


__all__ = ("DuplicateAuthorError",)

from django.db import models

from app.entities.models import ID


class AuthorManager(models.Manager):
    pass


class Author(models.Model):
    objects = AuthorManager()

    class Meta:
        db_table = "authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    author_id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)

    @property
    def book_ids(self, /) -> list[ID]:
        books = self.books.all()
        book_ids = [i.book_id for i in books]
        return book_ids

from django.db import models

from app.entities.models import ID
from app_api_v1.models import Author


class BookManager(models.Manager):
    pass


class Book(models.Model):
    objects = BookManager()

    class Meta:
        db_table = "books"
        verbose_name = "Book"
        verbose_name_plural = "Books"

    authors = models.ManyToManyField(Author, related_name="books")
    book_id = models.UUIDField(primary_key=True)
    title = models.TextField()

    @property
    def author_ids(self, /) -> list[ID]:
        authors = self.authors.all()
        author_ids = [i.author_id for i in authors]
        return author_ids

from django.db import models

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
    id = models.UUIDField(primary_key=True)  # noqa: A003,VNE003
    title = models.TextField()

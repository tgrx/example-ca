from django.db import models

from app_api_v1.models import Author


class BookManager(models.Manager):
    pass


class Book(models.Model):
    objects = BookManager()

    authors = models.ManyToManyField(Author, related_name="books")
    id = models.UUIDField(primary_key=True)  # noqa: A003,VNE003
    title = models.TextField()

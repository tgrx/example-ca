from django.db import models


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

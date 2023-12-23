from sqlalchemy import create_engine

from app.entities.config import Config
from app.repos.sqlalchemy.author import AuthorRepo
from app.repos.sqlalchemy.book import BookRepo

engine = create_engine(Config().PRIMARY_DATABASE_URL)

xxx_author_repo = AuthorRepo(engine=engine)
xxx_book_repo = BookRepo(engine=engine)

__all__ = (
    "xxx_author_repo",
    "xxx_book_repo",
)

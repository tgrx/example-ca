from typing import final

from pydantic import StrictStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from app.entities import consts


@final
class Config(BaseSettings):
    """
    The app's config.
    Instantiate this to get values from .env / ENVs at once.
    Type conversions, prefix cutting, all included.
    """

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file_encoding="utf-8",
        env_file=consts.DIR_REPO / ".env",
        env_prefix="WEBAPP_",
        extra="ignore",
        frozen=True,
    )

    MODE_DEBUG: bool = False
    PRIMARY_DATABASE_URL: StrictStr
    SECRET_KEY: StrictStr
    TEST_URL: StrictStr


__all__ = ("Config",)

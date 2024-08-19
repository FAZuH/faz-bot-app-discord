import os
from typing import Callable

from dotenv import load_dotenv


class Properties:

    # Application constants
    AUTHOR = "FAZuH"
    VERSION = "0.0.1"
    LOG_DIR = "./logs"

    # .env
    ADMIN_DISCORD_ID: int
    DISCORD_LOG_WEBHOOK: str
    DISCORD_STATUS_WEBHOOK: str
    FAZDB_DB_MAX_RETRIES: int
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    FAZDB_DB_NAME: str

    @classmethod
    def setup(cls) -> None:
        """Bootstraps application properties."""
        cls.__read_env()

    @classmethod
    def __read_env(cls) -> None:
        load_dotenv()
        cls.ADMIN_DISCORD_ID = cls._must_get_env("ADMIN_DISCORD_ID", int)
        cls.DISCORD_LOG_WEBHOOK = cls._must_get_env("FAZDB_DISCORD_LOG_WEBHOOK")
        cls.DISCORD_STATUS_WEBHOOK = cls._must_get_env("FAZDB_DISCORD_STATUS_WEBHOOK")
        cls.FAZDB_DB_MAX_RETRIES = cls._must_get_env("FAZDB_DB_MAX_RETRIES", int)
        cls.MYSQL_HOST = cls._must_get_env("MYSQL_HOST")
        cls.MYSQL_PORT = cls._must_get_env("MYSQL_PORT", int)
        cls.MYSQL_USERNAME = cls._must_get_env("MYSQL_USER")
        cls.MYSQL_PASSWORD = cls._must_get_env("MYSQL_PASSWORD")
        cls.FAZDB_DB_NAME = cls._must_get_env("MYSQL_FAZDB_DATABASE")

    @staticmethod
    def _must_get_env[T](key: str, type_strategy: Callable[[str], T] = str) -> T:
        try:
            env = os.getenv(key)
            return type_strategy(env)  # type: ignore
        except ValueError:
            raise ValueError(f"Failed parsing environment variable {key} into type {type_strategy}")

import os
from typing import Any


def configure_database_url(config: Any) -> None:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)

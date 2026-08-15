from app.migration_config import configure_database_url


def test_configure_database_url_uses_database_url_environment(monkeypatch) -> None:
    database_url = "postgresql+psycopg://user:password@postgres:5432/app"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = _Config(
        "postgresql+psycopg://user:password@localhost:5432/app"
    )

    configure_database_url(config)

    assert config.get_main_option("sqlalchemy.url") == database_url


class _Config:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def get_main_option(self, key: str) -> str:
        assert key == "sqlalchemy.url"
        return self.database_url

    def set_main_option(self, key: str, value: str) -> None:
        assert key == "sqlalchemy.url"
        self.database_url = value

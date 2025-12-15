from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    LOG_JSON_FORMAT: bool = True
    LOG_LEVEL: str = "DEBUG"
    SWAGGER: bool = True
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    API_TORTOISE_MODELS: list[str] = Field(
        default_factory=lambda: [
            "apps.companies.models",
            "apps.users.models",
        ]
    )

class PostgresApiSettings(BaseSettings):
    USER: str = "postgres"
    HOST: str = "postgres-specter"
    PORT: int = 5432
    NAME: str = "postgres"
    PASS: str = "postgres"

    MIN_CONN_SIZE: int = 1
    MAX_CONN_SIZE: int = 10

    @property
    def POSTGRES_DSN(self):
        return f"postgres://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"

    class Config:
        env_prefix = "API_POSTGRES_"

class ClickhouseSettings(BaseSettings):
    USER: str = "clickhouse"
    HOST: str = "clickhouse"
    PORT: int = 8123
    NAME: str = "default"
    PASS: str | int = "clickhouse"
    SECURE: bool = False
    VERIFY: bool = False
    CA_CERT: str | None = None

    MIN_CONN_SIZE: int = 1
    MAX_CONN_SIZE: int = 10

    @property
    def CLICKHOUSE_DSN(self):
        return f"clickhouse+native://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"

    class Config:
        env_prefix = "CLICKHOUSE_"


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    postgres_api: PostgresApiSettings = PostgresApiSettings()
    clickhouse: ClickhouseSettings = ClickhouseSettings()

@lru_cache
def get_settings() -> "Settings":
    return Settings()

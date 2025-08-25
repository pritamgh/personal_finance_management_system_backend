from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class is used to load and validate configuration variables
    for the application. It leverages Pydantic to automatically load
    configuration from environment variables.
    """
    POSTGRESQLDB_HOST: str
    POSTGRESQLDB_PORT: int
    POSTGRESQLDB_USER: str
    POSTGRESQLDB_PASSWORD: str
    POSTGRESQLDB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Configuration to load environment variables from the ".env" file
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    """
    Using functools' lru_cache to ensure that the settings are loaded
    only once and cached. This function will return the settings instance,
    ensuring efficient memory usage.
    """
    return Settings()


class Config:
    """
    Config class encapsulates the settings related to the application's
    database connection. It uses the settings retrieved from the
    'get_settings' function to construct a PostgreSQL URL.
    """
    settings = get_settings()
    POSTGRESQLDB_URL: str = "postgresql://%s:%s@%s:%s/%s" % (
        settings.POSTGRESQLDB_USER,
        settings.POSTGRESQLDB_PASSWORD,
        settings.POSTGRESQLDB_HOST,
        settings.POSTGRESQLDB_PORT,
        settings.POSTGRESQLDB_NAME,
    )

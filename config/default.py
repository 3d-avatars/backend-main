from os import environ
from passlib.context import CryptContext

from pydantic_settings import BaseSettings


class DefaultSettings(BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments: for development, testing and production.
    But in this situation, we only have standard settings for local development.
    """

    # App settings
    ENV: str = environ.get("ENV", "local")
    PATH_PREFIX: str = environ.get("PATH_PREFIX", "/api/v1")
    APP_HOST: str = environ.get("APP_HOST", "http://127.0.0.1")
    APP_PORT: int = int(environ.get("APP_PORT", 8080))

    SECRET_KEY: str = environ.get("SECRET_KEY", "")
    REFRESH_SECRET_KEY: str = environ.get("REFRESH_SECRET_KEY", "")
    HASH_ALGORITHM: str = environ.get("HASH_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 24)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 168)

    # Postgres
    POSTGRES_DB: str = environ.get("POSTGRES_DB", "task_db")
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST", "postgres")
    POSTGRES_HOST_FOR_MIGRATIONS: str = environ.get("POSTGRES_HOST_FOR_MIGRATIONS", "localhost")
    POSTGRES_USER: str = environ.get("POSTGRES_USER", "user")
    POSTGRES_PORT: int = int(environ.get("POSTGRES_PORT", "5432")[-4:])
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD", "hackme")
    DB_CONNECT_RETRY: int = environ.get("DB_CONNECT_RETRY", 20)
    DB_POOL_SIZE: int = environ.get("DB_POOL_SIZE", 15)

    #Minio
    MINIO_HOST: str = environ.get("MINIO_HOST", "minio")
    MINIO_PROD_HOST: str =environ.get("MINIO_PROD_HOST", "minio")
    MINIO_API_PORT: int = int(environ.get("MINIO_API_PORT", "9000")[-4:])
    MINIO_ROOT_USER: str = environ.get("MINIO_ROOT_USER", "task_user")
    MINIO_ROOT_PASSWORD: str = environ.get("MINIO_ROOT_PASSWORD", "hackme_task_user")
    MINIO_IMAGES_BUCKET: str = environ.get("MINIO_IMAGES_BUCKET", "source-images")
    MINIO_GLB_BUCKET: str = environ.get("MINIO_GLB_BUCKET", "glb-files")

    # RabbitMQ
    RABBITMQ_HOST: str = environ.get("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: int = int(environ.get("RABBITMQ_PORT", "5672")[-4:])
    RABBITMQ_DEFAULT_USER: str = environ.get("RABBITMQ_DEFAULT_USER", "task_user")
    RABBITMQ_DEFAULT_PASSWORD: str = environ.get("RABBITMQ_DEFAULT_PASS", "hackme")
    RABBITMQ_TASKS_QUEUE: str = environ.get("RABBITMQ_TASKS_QUEUE", "tasks")
    RABBITMQ_TASKS_RESULTS_QUEUE: str = environ.get("RABBITMQ_TASKS_RESULTS_QUEUE", "task_results")

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with tasks.
        """
        return {
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
        }

    @property
    def database_settings_for_migrations(self) -> dict:
        """
        Get all settings for connection with tasks.
        """
        return {
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST_FOR_MIGRATIONS,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with tasks.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    @property
    def database_uri_for_migrations(self) -> str:
        """
        Get uri for connection with tasks.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings_for_migrations,
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with tasks.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra='allow'

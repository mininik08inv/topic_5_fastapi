from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv
import os


class DatabaseConfig(BaseSettings):
    host: str = Field(..., alias="DB_HOST")
    database: str = Field(..., alias="DB_DATABASE")
    user: str = Field(..., alias="DB_USER")
    password: str = Field(..., alias="DB_PASSWORD")
    port: str = Field(..., alias="DB_PORT")

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="DB_"
    )


class RedisConfig(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="REDIS_"
    )


class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)

    @classmethod
    def load(cls) -> "Config":
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"

        if not env_path.exists():
            raise FileNotFoundError(f".env file not found at: {env_path}")

        load_dotenv(env_path, override=True)

        return cls()
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class RedisConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    # cache_reset_time: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def REDIS_URL(self):
        return f"redis://{config.redis.REDIS_HOST}:{config.redis.REDIS_PORT}"


class LoggingConfig(BaseSettings):
    loging_default_lavel: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
    )


class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    log: LoggingConfig = Field(default_factory=LoggingConfig)


config = Config()

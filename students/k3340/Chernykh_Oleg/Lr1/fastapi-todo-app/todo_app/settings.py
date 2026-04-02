from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    server_host: str = "localhost"
    server_port: int = 8000
    db_url: str = Field(env="DATABASE_URL")
    secret_key: str = Field(env="SECRET_KEY")
    reload: bool = True
    workers: int = 4
    jwt_token_expiration: int = 1800
    jwt_algorithm: str = Field(env="JWT_ALGORITHM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

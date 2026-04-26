from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    database_host: str = "postgres"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "todos"
    secret_key: str = "secret"
    jwt_token_expiration: int = 1800
    jwt_algorithm: str = "HS256"
    parser_host: str = "web-parser"
    parser_port: int = 8080
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "redispass"

    @property
    def database_url(self) -> str:
        return f"postgres://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    @property
    def parser_url(self) -> str:
        return f"http://{self.parser_host}:{self.parser_port}/parse"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["todo_app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

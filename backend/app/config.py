from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/tickets.db"
    debug: bool = False
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    token_expire_hours: int = 24
    admin_username: str = "admin"
    admin_password: str = "admin"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

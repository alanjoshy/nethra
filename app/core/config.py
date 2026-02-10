from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "nethra Backend"
    database_url: str
    auto_migrate: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()

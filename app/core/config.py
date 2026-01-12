from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentinel Backend"

    class Config:
        env_file = ".env"


settings = Settings()

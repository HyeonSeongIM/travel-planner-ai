from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Travel Planner AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    model_config = {"env_file": ".env"}


settings = Settings()

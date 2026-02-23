from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RestaurantAPI"
    APP_ENV: str = "dev"
    APP_VERSION: str = "1.0"

    DATABASE_URL: str

    JWT_SECRET: str = "change-me-please"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

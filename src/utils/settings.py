from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot settings
    BOT_TOKEN: SecretStr
    
    # AI settings
    GEMINI_API_KEY: SecretStr

    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "default"
    REDIS_PASSWORD: SecretStr
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

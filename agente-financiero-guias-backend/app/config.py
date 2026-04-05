from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AFIP_ENV: str = "homo"
    ENCRYPTION_KEY: str
    ALLOWED_ORIGINS: str = "*"
    GCS_BUCKET_NAME: str = "agente-financiero-files" # Default value if not in .env
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    AFIP_FERNET_KEY: str = ""
    AFIP_ENVIRONMENT: str = "homologacion"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

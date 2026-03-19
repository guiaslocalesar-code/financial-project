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

    # Storage Settings
    STORAGE_BACKEND: str = "local" # local or supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "logos"

    @property
    def sync_database_url(self) -> str:
        # Useful for tools that don't support asyncpg yet (if any)
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def async_database_url(self) -> str:
        # Ensure the URL has the +asyncpg prefix for SQLAlchemy
        url = self.DATABASE_URL
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

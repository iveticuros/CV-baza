from typing import List

from cryptography.fernet import Fernet
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str

    PII_ENCRYPTION_KEY: str

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    ENVIRONMENT: str = "development"

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = False
    SMTP_FROM_EMAIL: str = "noreply@cv.best.rs"
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    EMAIL_VERIFY_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 2

    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15

    CV_UPLOAD_MAX_BYTES: int = 5 * 1024 * 1024
    CV_STORAGE_DIR: str = "./data/cv_uploads"

    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 5
    DOWNLOAD_RATE_LIMIT_PER_MINUTE: int = 20

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def cookie_secure(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cookie_samesite(self) -> str:
        return "none" if self.ENVIRONMENT == "production" else "lax"

    @field_validator("PII_ENCRYPTION_KEY")
    @classmethod
    def fernet_key_valid(cls, v: str) -> str:
        v = (v or "").strip()
        try:
            Fernet(v.encode("utf-8"))
        except Exception as e:
            raise ValueError(
                "PII_ENCRYPTION_KEY must be a valid Fernet key; generate with Python: "
                "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
            ) from e
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

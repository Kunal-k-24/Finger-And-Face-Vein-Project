from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/biometric_db"
    POSTGRES_DB: str = "biometric_db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "pass"

    # JWT Security
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Homomorphic Encryption (TenSEAL)
    HE_POLY_MODULUS_DEGREE: int = 8192

    # Differential Privacy (Opacus)
    DP_TARGET_EPSILON: float = 3.0
    DP_TARGET_DELTA: float = 1e-5
    DP_MAX_GRAD_NORM: float = 1.0

    # Federated Learning (Flower)
    FL_SERVER_ADDRESS: str = "localhost:8080"
    FL_NUM_ROUNDS: int = 10

    # Biometric Threshold
    SIMILARITY_THRESHOLD: float = 0.75

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

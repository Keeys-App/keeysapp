from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://locales_user:locales_password@localhost:5432/locales_db"
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Locales API"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Railway specific
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""


settings = Settings()

# Debug: print database URL (without password for security)
if settings.database_url:
    # Hide password in logs
    import re
    safe_url = re.sub(r':[^:@]+@', ':***@', settings.database_url)
    print(f"Database URL: {safe_url}")
else:
    print("No DATABASE_URL found!")

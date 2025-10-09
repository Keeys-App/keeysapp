from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database - Railway will provide DATABASE_URL automatically
    DATABASE_URL: str
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Locales API"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 525600  # 1 year (365 days * 24 hours * 60 minutes)
    
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
if settings.DATABASE_URL:
    # Hide password in logs
    import re
    safe_url = re.sub(r':[^:@]+@', ':***@', settings.DATABASE_URL)
    print(f"Database URL: {safe_url}")
else:
    print("No DATABASE_URL found!")

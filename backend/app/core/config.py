from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database - Railway will provide DATABASE_URL automatically
    DATABASE_URL: str
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Keeys API"
    
    # Security
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 525600  # 1 year (365 days * 24 hours * 60 minutes)
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Railway specific
    port: int = 8000
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_text_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 4000
    openai_temperature: float = 1.0
    openai_timeout: int = 120
    
    # Brevo (Email)
    brevo_api_key: Optional[str] = None
    brevo_sender_email: str = "noreply@example.com"
    brevo_sender_name: str = "Keeys App"
    
    # Application URL (for email links)
    app_url: str = "http://localhost:3000"
    
    # GitHub App
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_callback_url: str = "http://localhost:8000/api/github/callback"
    github_app_slug: Optional[str] = None  # App name from URL: github.com/apps/{slug}
    
    # Token encryption key for storing GitHub tokens (Fernet key)
    token_encryption_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
        extra = "ignore"  # Ignore unknown fields from .env


settings = Settings()

# Debug: print database URL (without password for security)
if settings.DATABASE_URL:
    # Hide password in logs
    import re
    safe_url = re.sub(r':[^:@]+@', ':***@', settings.DATABASE_URL)
    print(f"Database URL: {safe_url}")
else:
    print("No DATABASE_URL found!")

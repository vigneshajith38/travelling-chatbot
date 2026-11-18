import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from backend directory and root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "backend" / ".env")
load_dotenv(".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "WanderWise API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "wanderwise_super_secret_jwt_key_2026_travel_ai")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wanderwise.db")
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    # External APIs
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    OSRM_ROUTING_URL: str = "https://router.project-osrm.org/route/v1/driving"
    
    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()

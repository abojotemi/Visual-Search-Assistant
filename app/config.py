# config.py
import logging
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings and configuration"""
    APP_NAME: str = "Fit AI"
    DEBUG: bool = False
    GOOGLE_AI_MODEL: str = "gemini-1.5-flash"
    BLIP_MODEL: str = "Salesforce/blip-image-captioning-base"
    LOG_LEVEL: str = "INFO"
    DATA_DIR: Path = Path("data")
    
    class Config:
        env_file = ".env"

settings = Settings()

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fitness_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

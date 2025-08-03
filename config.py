import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file if exists
load_dotenv()

class Config:
    """Application configuration"""
    
    # Runway ML Configuration
    RUNWAY_ML_API_KEY: str = os.getenv("RUNWAY_ML_API_KEY", "")
    RUNWAY_ML_BASE_URL: str = "https://api.runwayml.com/v1"
    
    # OpenAI Configuration (for Whisper and GPT-4)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    WHISPER_API_KEY: str = os.getenv("WHISPER_API_KEY", OPENAI_API_KEY)  # Use OpenAI key for Whisper
    GPT4_API_KEY: str = os.getenv("GPT4_API_KEY", OPENAI_API_KEY)  # Use OpenAI key for GPT-4
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        missing_keys = []
        
        if not cls.RUNWAY_ML_API_KEY or cls.RUNWAY_ML_API_KEY == "your_runway_ml_api_key_here":
            missing_keys.append("RUNWAY_ML_API_KEY")
        
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your_openai_api_key_here":
            missing_keys.append("OPENAI_API_KEY")
        
        if missing_keys:
            print("⚠️  WARNING: Some API keys are not configured")
            print("Please set the following environment variables:")
            for key in missing_keys:
                print(f"  {key}=your_actual_api_key_here")
            print("\nNote: Some services may not work without proper API keys")
    
    @classmethod
    def get_runway_headers(cls) -> dict:
        """Get Runway ML API headers"""
        if not cls.RUNWAY_ML_API_KEY or cls.RUNWAY_ML_API_KEY == "your_runway_ml_api_key_here":
            raise ValueError("RUNWAY_ML_API_KEY is not properly configured")
        
        return {
            "Authorization": f"Bearer {cls.RUNWAY_ML_API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_openai_headers(cls) -> dict:
        """Get OpenAI API headers"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your_openai_api_key_here":
            raise ValueError("OPENAI_API_KEY is not properly configured")
        
        return {
            "Authorization": f"Bearer {cls.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (without sensitive data)"""
        print("🔧 Current Configuration:")
        print(f"  HOST: {cls.HOST}")
        print(f"  PORT: {cls.PORT}")
        print(f"  LOG_LEVEL: {cls.LOG_LEVEL}")
        print(f"  RUNWAY_ML_BASE_URL: {cls.RUNWAY_ML_BASE_URL}")
        
        # Check API keys
        if cls.RUNWAY_ML_API_KEY and cls.RUNWAY_ML_API_KEY != "your_runway_ml_api_key_here":
            print(f"  RUNWAY_ML_API_KEY: {'*' * len(cls.RUNWAY_ML_API_KEY)}")
        else:
            print("  RUNWAY_ML_API_KEY: Not configured")
        
        if cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "your_openai_api_key_here":
            print(f"  OPENAI_API_KEY: {'*' * len(cls.OPENAI_API_KEY)}")
        else:
            print("  OPENAI_API_KEY: Not configured") 
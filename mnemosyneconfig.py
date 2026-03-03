"""
Mnemosyne Configuration Management
Centralized configuration with validation and environment-aware settings
"""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings
from typing import Optional, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class MnemosyneConfig(BaseSettings):
    """Validated configuration for Mnemosyne caching system"""
    
    # DeepSeek API Configuration
    DEEPSEEK_API_KEY: Optional[str] = Field(None, description="API key for DeepSeek service")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", description="DeepSeek API endpoint")
    DEEPSEEK_TIMEOUT: int = Field(30, gt=0, description="API timeout in seconds")
    DEEPSEEK_MAX_RETRIES: int = Field(3, ge=0, le=5, description="Maximum retry attempts")
    
    # Cache Configuration
    CACHE_ENABLED: bool = Field(True, description="Enable caching layer")
    CACHE_TTL_SECONDS: int = Field(3600, gt=0, description="Cache time-to-live")
    CACHE_FALLBACK_ENABLED: bool = Field(True, description="Enable fallback to cached responses")
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = Field(..., description="Firebase project ID")
    FIREBASE_CREDENTIALS_PATH: Optional[str] = Field(None, description="Path to service account key")
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = Field(5, gt=0, description="Maximum concurrent API calls")
    REQUEST_TIMEOUT: int = Field(45, gt=0, description="Overall request timeout")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(True, description="Enable performance metrics collection")
    LOG_LEVEL: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # Redis Configuration (Optional fallback)
    REDIS_URL: Optional[str] = Field(None, description="Redis connection URL")
    REDIS_ENABLED: bool = Field(False, description="Enable Redis as secondary cache")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @classmethod
    def load(cls) -> "MnemosyneConfig":
        """Load and validate configuration with error handling"""
        try:
            config = cls()
            logger.info("Configuration loaded successfully", 
                       cache_enabled=config.CACHE_ENABLED,
                       firebase_project=config.FIREBASE_PROJECT_ID[:8] + "..." if config.FIREBASE_PROJECT_ID else None)
            return config
        except ValidationError as e:
            logger.error("Configuration validation failed", errors=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected configuration error", error=str(e))
            raise RuntimeError(f"Failed to load configuration: {str(e)}") from e
    
    def validate_api_credentials(self) -> bool:
        """Validate that required API credentials are present"""
        if not self.DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API key not configured")
            return False
        
        if not self.FIREBASE_PROJECT_ID:
            logger.error("Firebase project ID is required")
            return False
            
        return True
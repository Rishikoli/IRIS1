"""
Project IRIS - Application Configuration
Loads settings from environment variables
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    
    # CORS
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")
    
    # API Keys
    fmp_api_key: str = Field(..., env="FMP_API_KEY")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    nse_api_key: Optional[str] = Field(default=None, env="NSE_API_KEY")
    bse_api_key: Optional[str] = Field(default=None, env="BSE_API_KEY")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # ChromaDB
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8001, env="CHROMA_PORT")
    chroma_persist_directory: str = Field(default="./data/chromadb", env="CHROMA_PERSIST_DIRECTORY")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    celery_task_time_limit: int = Field(default=900, env="CELERY_TASK_TIME_LIMIT")
    
    # Intel Hardware
    openvino_enabled: bool = Field(default=True, env="OPENVINO_ENABLED")
    intel_pytorch_enabled: bool = Field(default=True, env="INTEL_PYTORCH_ENABLED")
    openvino_device: str = Field(default="AUTO", env="OPENVINO_DEVICE")
    intel_pytorch_version: str = Field(default="2.6.0", env="INTEL_PYTORCH_VERSION")
    
    # FMP API
    fmp_base_url: str = Field(default="https://financialmodelingprep.com/api/v3", env="FMP_BASE_URL")
    fmp_rate_limit_per_day: int = Field(default=250, env="FMP_RATE_LIMIT_PER_DAY")
    fmp_rate_limit_per_minute: int = Field(default=4, env="FMP_RATE_LIMIT_PER_MINUTE")
    fmp_timeout: int = Field(default=30, env="FMP_TIMEOUT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # File Storage
    upload_folder: str = Field(default="./data/uploads", env="UPLOAD_FOLDER")
    report_folder: str = Field(default="./data/reports", env="REPORT_FOLDER")
    pdf_folder: str = Field(default="./data/pdfs", env="PDF_FOLDER")
    
    # Feature Flags
    enable_sentiment_analysis: bool = Field(default=True, env="ENABLE_SENTIMENT_ANALYSIS")
    enable_peer_benchmarking: bool = Field(default=True, env="ENABLE_PEER_BENCHMARKING")
    enable_regulatory_monitoring: bool = Field(default=True, env="ENABLE_REGULATORY_MONITORING")
    enable_qa_system: bool = Field(default=True, env="ENABLE_QA_SYSTEM")
    
    # Performance
    document_chunk_size: int = Field(default=512, env="DOCUMENT_CHUNK_SIZE")
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    max_concurrent_jobs: int = Field(default=10, env="MAX_CONCURRENT_JOBS")
    
    # Cache TTL
    cache_ttl_financial_data: int = Field(default=86400, env="CACHE_TTL_FINANCIAL_DATA")
    cache_ttl_company_profile: int = Field(default=604800, env="CACHE_TTL_COMPANY_PROFILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()

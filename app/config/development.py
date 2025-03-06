from app.config.base import BaseConfig
import os

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    ELASTICSEARCH_INDEX = f"{BaseConfig.ELASTICSEARCH_INDEX_PREFIX}dev"
    
    # Explicitly set database URI for development
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///pickleball.db') 
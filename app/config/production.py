from app.config.base import BaseConfig
import os

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    ELASTICSEARCH_INDEX = f"{BaseConfig.ELASTICSEARCH_INDEX_PREFIX}prod"
    
    # Explicitly set database URI for production
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') 
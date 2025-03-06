from app.config.base import BaseConfig

class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use an in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ELASTICSEARCH_INDEX = f"{BaseConfig.ELASTICSEARCH_INDEX_PREFIX}test" 
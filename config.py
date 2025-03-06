import os
import sys
from pathlib import Path

# Get database URI
def get_database_uri():
    """Determine the database URI based on environment and create necessary directories."""
    # Use DATABASE_URL from environment if provided
    if os.environ.get('DATABASE_URL'):
        # If using SQLite, ensure correct path format and directory exists
        if 'sqlite:///' in os.environ.get('DATABASE_URL', ''):
            db_path = os.environ.get('DATABASE_URL').replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}", file=sys.stderr)
        return os.environ.get('DATABASE_URL')
    
    # Default to SQLite in instance directory
    instance_dir = Path('instance').absolute()
    instance_dir.mkdir(exist_ok=True, parents=True)
    db_file = instance_dir / 'pickleball.db'
    return f'sqlite:///{db_file.as_posix()}'


class Config:
    """Base configuration."""
    # Secret keys
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # In production, ensure proper secret keys
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or Config.JWT_SECRET_KEY
    
    def __init__(self):
        # Log database configuration in production
        print(f"Production database: {self.SQLALCHEMY_DATABASE_URI}", file=sys.stderr)
        
        # Warn if using default keys in production
        if self.SECRET_KEY == Config.SECRET_KEY or self.JWT_SECRET_KEY == Config.JWT_SECRET_KEY:
            print("WARNING: Using default secret keys in production is not secure!", file=sys.stderr)
            print("Set SECRET_KEY and JWT_SECRET_KEY environment variables.", file=sys.stderr)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionary to easily select the configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
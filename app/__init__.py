import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """Application factory for Flask app"""
    app = Flask(__name__)
    
    # Configure the app
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'development':
        app.config.from_object('app.config.development.DevelopmentConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.testing.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('app.config.production.ProductionConfig')
    
    # Ensure DATABASE_URI is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///pickleball.db')
    
    # Enable CORS
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.games import games_bp
    from app.api.courts import courts_bp
    from app.api.chat import chat_bp
    from app.api.search import search_bp
    from app.api import frontend_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(games_bp, url_prefix='/api/games')
    app.register_blueprint(courts_bp, url_prefix='/api/courts')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(frontend_bp)
    
    # Create database tables on app startup
    with app.app_context():
        db.create_all()
    
    return app 
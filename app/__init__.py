import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

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
    
    # Import and use configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure instance directory exists
    Path(app.instance_path).mkdir(exist_ok=True, parents=True)
    
    # Enable CORS
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Log the database URI being used
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}", file=sys.stderr)
    
    # Register error handlers
    @app.errorhandler(500)
    def handle_500_error(e):
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
        
    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize database tables
    init_database(app)
    
    return app

def register_blueprints(app):
    """Register Flask blueprints"""
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
    
def init_database(app):
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error creating database tables: {str(e)}", file=sys.stderr)
        # Don't fail the app initialization if database creation fails
        # In production with a hosted database, tables should be created separately 
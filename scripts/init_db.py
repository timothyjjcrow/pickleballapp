import os
import sys
import importlib.util

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables directly
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'your_secret_key'
os.environ['DATABASE_URL'] = 'sqlite:///pickleball.db'
os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
os.environ['CORS_ORIGINS'] = 'http://localhost:5000'
os.environ['SOCKET_HOST'] = 'localhost'
os.environ['SOCKET_PORT'] = '5001'

# Patch the load_dotenv function to do nothing
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: None

from app import create_app, db

def init_db():
    """Initialize the database by creating all tables."""
    app = create_app('development')
    
    # Set the database URI directly in the app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pickleball.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 
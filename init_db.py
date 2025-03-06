#!/usr/bin/env python
"""
Database initialization script for Pickleball app.
This script creates the necessary database and tables.
"""
import os
import sys
import sqlite3
from pathlib import Path
from app import db, create_app

def init_database():
    """Initialize the database with tables."""
    # Configure environment
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"Initializing database in {env} environment...")
    
    # For SQLite, ensure the file exists first
    if not os.environ.get('DATABASE_URL') or 'sqlite:///' in os.environ.get('DATABASE_URL'):
        # Get database path
        if os.environ.get('DATABASE_URL'):
            db_path = os.environ.get('DATABASE_URL').replace('sqlite:///', '')
        else:
            # Default to instance/pickleball.db
            instance_dir = Path('instance').absolute()
            instance_dir.mkdir(exist_ok=True, parents=True)
            db_path = instance_dir / 'pickleball.db'
            db_uri = f'sqlite:///{db_path.as_posix()}'
            os.environ['DATABASE_URL'] = db_uri
        
        # Create the SQLite file if it doesn't exist
        if not os.path.exists(db_path):
            try:
                print(f"Creating SQLite database at: {db_path}")
                # Create parent directory if it doesn't exist
                parent_dir = os.path.dirname(db_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                
                # Create an empty database file
                connection = sqlite3.connect(str(db_path))
                connection.close()
                print("Database file created.")
            except Exception as e:
                print(f"Error creating database file: {str(e)}", file=sys.stderr)
                return False
    
    # Create the Flask app
    try:
        app = create_app(env)
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"Tables created: {', '.join(tables)}")
            else:
                print("Warning: No tables were created", file=sys.stderr)
                
            return True
    except Exception as e:
        print(f"Error creating database schema: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("Database initialization complete.")
    else:
        print("Database initialization failed.", file=sys.stderr)
        sys.exit(1) 
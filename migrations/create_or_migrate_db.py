#!/usr/bin/env python
"""
Database migration script for the Pickleball app.
This script initializes or migrates the database on Heroku or other cloud platforms.
"""
import os
import sys
from pathlib import Path
from flask_migrate import Migrate, upgrade

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, create_app

def create_or_migrate_db():
    """Initialize or migrate the database on Heroku or other cloud platforms."""
    env = os.environ.get('FLASK_ENV', 'production')
    print(f"Starting database initialization/migration in {env} environment...")
    
    # Create the Flask app with the production configuration
    app = create_app(env)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            # Log database connection info (without credentials)
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgres' in db_url:
                # Mask credentials in the URL for logging
                masked_url = db_url.split('@')
                if len(masked_url) > 1:
                    print(f"Using database: postgres@{masked_url[1]}")
                else:
                    print(f"Using database: {db_url}")
            else:
                print(f"Using database: {db_url}")
                
            print("Running database migrations...")
            # Run database migrations
            upgrade()
            print("Database migrations completed successfully.")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("No tables found after migration. Creating all tables...")
                db.create_all()
                
                # Verify tables were created
                tables = inspector.get_table_names()
                if tables:
                    print(f"Tables created: {', '.join(tables)}")
                else:
                    print("Warning: Failed to create tables", file=sys.stderr)
                    return False
            else:
                print(f"Database contains tables: {', '.join(tables)}")
                
            return True
        except Exception as e:
            print(f"Error during database migration: {str(e)}", file=sys.stderr)
            # In production, we'll try to recover by creating tables directly
            try:
                print("Attempting to create tables directly...")
                db.create_all()
                
                # Verify tables were created
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                if tables:
                    print(f"Tables created: {', '.join(tables)}")
                    return True
                else:
                    print("Warning: No tables were created", file=sys.stderr)
                    return False
            except Exception as e2:
                print(f"Error creating tables: {str(e2)}", file=sys.stderr)
                return False

if __name__ == '__main__':
    print("Running database setup for cloud deployment...")
    success = create_or_migrate_db()
    if success:
        print("Database setup completed successfully.")
        sys.exit(0)
    else:
        print("Database setup failed.", file=sys.stderr)
        sys.exit(1) 
import os
import sys
import sqlite3
from pathlib import Path
from app import create_app

def setup_environment():
    """Set up environment variables and database for the application."""
    # Ensure instance directory exists
    instance_dir = Path('instance').absolute()
    instance_dir.mkdir(exist_ok=True, parents=True)

    # Get absolute path to database file with forward slashes for SQLite compatibility
    db_file = instance_dir / 'pickleball.db'
    db_uri = f'sqlite:///{db_file.as_posix()}'

    # Set default environment variables if not already set
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = db_uri
        print(f"Using database: {db_uri}")

    os.environ.setdefault('FLASK_APP', 'app')
    os.environ.setdefault('FLASK_ENV', 'development')

    # Ensure database file exists and is writable
    if not db_file.exists():
        try:
            # Create an empty database file
            print(f"Creating database file at: {db_file}")
            connection = sqlite3.connect(str(db_file))
            connection.close()
            print(f"Created database file.")
        except Exception as e:
            print(f"Error creating database file: {str(e)}", file=sys.stderr)
            return False

    return True

def main():
    """Main entry point for the application."""
    # Setup environment and database
    if not setup_environment():
        print("Failed to set up environment. Exiting.", file=sys.stderr)
        sys.exit(1)

    try:
        # Create and run the Flask app
        app = create_app()
        
        print(f"Starting Flask application...")
        print(f"Database URL: {os.environ.get('DATABASE_URL')}")
        print(f"Environment: {os.environ.get('FLASK_ENV')}")
        
        # Run the app if executed directly (not imported)
        if __name__ == '__main__':
            app.run(host="0.0.0.0", port=5000, debug=(os.environ.get('FLASK_ENV') == 'development'))
            
        return app
    except Exception as e:
        print(f"Error starting application: {str(e)}", file=sys.stderr)
        sys.exit(1)

# Execute if run directly
if __name__ == '__main__':
    main() 
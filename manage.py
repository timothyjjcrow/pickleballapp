#!/usr/bin/env python
"""
Management script for the Pickleball application.
This script provides commands for development, testing, and deployment.
"""
import os
import sys
import argparse
import shutil
from pathlib import Path

def ensure_instance_dir():
    """Ensure the instance directory exists."""
    instance_dir = Path('instance').absolute()
    instance_dir.mkdir(exist_ok=True, parents=True)
    return instance_dir

def run_app(args):
    """Run the Flask application."""
    # Set up the environment
    os.environ['FLASK_APP'] = 'wsgi.py'
    if args.env:
        os.environ['FLASK_ENV'] = args.env
    else:
        os.environ.setdefault('FLASK_ENV', 'development')
    
    if args.debug:
        os.environ['FLASK_DEBUG'] = '1'
    
    if args.port:
        os.environ['PORT'] = str(args.port)
    
    # Import here to avoid circular imports
    from run import main
    main()

def setup_db(args):
    """Initialize or reset the database."""
    # Set up the environment
    if args.env:
        os.environ['FLASK_ENV'] = args.env
    else:
        os.environ.setdefault('FLASK_ENV', 'development')
    
    # Import here to avoid circular imports
    from init_db import init_database
    success = init_database()
    if not success:
        sys.exit(1)

def run_migrations(args):
    """Run database migrations."""
    # Set up the environment
    if args.env:
        os.environ['FLASK_ENV'] = args.env
    else:
        os.environ.setdefault('FLASK_ENV', 'production')
    
    # Import here to avoid circular imports
    from migrations.create_or_migrate_db import create_or_migrate_db
    success = create_or_migrate_db()
    if not success:
        sys.exit(1)

def run_tests(args):
    """Run the test suite."""
    # Set up the environment for testing
    os.environ['FLASK_ENV'] = 'testing'
    
    # Import unittest here to avoid circular imports
    import unittest
    
    # Discover and run tests
    if args.test_path:
        test_path = args.test_path
    else:
        test_path = 'test_*.py'
    
    print(f"Running tests from: {test_path}")
    test_suite = unittest.defaultTestLoader.discover('.', pattern=test_path)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    if not result.wasSuccessful():
        sys.exit(1)

def create_env_file(args):
    """Create or update .env file with default values."""
    env_path = Path('.env')
    
    # Default values
    env_vars = {
        'FLASK_APP': 'wsgi.py',
        'FLASK_ENV': args.env or 'development',
        'SECRET_KEY': 'your-secret-key-change-in-production',
        'JWT_SECRET_KEY': 'your-jwt-secret-key-change-in-production',
    }
    
    # Add database URL if provided
    if args.db_url:
        env_vars['DATABASE_URL'] = args.db_url
    
    # Check if file exists
    if env_path.exists() and not args.force:
        print(".env file already exists. Use --force to overwrite.")
        return
    
    # Write the file
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f".env file created at {env_path.absolute()}")

def main():
    parser = argparse.ArgumentParser(description='Pickleball Application Management')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the Flask application')
    run_parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                           help='Environment to run in')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    run_parser.add_argument('--port', type=int, help='Port to run on')
    run_parser.set_defaults(func=run_app)
    
    # DB setup command
    db_parser = subparsers.add_parser('setup-db', help='Initialize the database')
    db_parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                          help='Environment to run in')
    db_parser.set_defaults(func=setup_db)
    
    # Migrations command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    migrate_parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                              help='Environment to run in')
    migrate_parser.set_defaults(func=run_migrations)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--test-path', help='Path to test files')
    test_parser.set_defaults(func=run_tests)
    
    # Env command
    env_parser = subparsers.add_parser('create-env', help='Create .env file')
    env_parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                           help='Environment to run in')
    env_parser.add_argument('--db-url', help='Database URL')
    env_parser.add_argument('--force', action='store_true', help='Overwrite existing file')
    env_parser.set_defaults(func=create_env_file)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 
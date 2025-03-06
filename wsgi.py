import os
from app import create_app

# Set environment to production
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application
application = create_app('production')

# For compatibility with some WSGI servers that expect 'app'
app = application

if __name__ == "__main__":
    # Use Waitress for Windows compatibility
    from waitress import serve
    print("Starting Waitress server...")
    serve(application, host="0.0.0.0", port=8000) 
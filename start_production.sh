#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables for production
export FLASK_ENV=production
export FLASK_APP=wsgi.py

# You should set these environment variables before running in production
# export SECRET_KEY=your-secret-key
# export JWT_SECRET_KEY=your-jwt-secret-key
# export DATABASE_URL=sqlite:///pickleball.db  # Or your production database URL

# Start Gunicorn server
# Adjust the number of workers based on your server's capacity
# A common formula is (2 x number of cores) + 1
gunicorn --workers=4 --bind=0.0.0.0:8000 --log-level=info wsgi:app 
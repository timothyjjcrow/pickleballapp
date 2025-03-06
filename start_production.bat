@echo off
REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Set environment variables for production
set FLASK_ENV=production
set FLASK_APP=wsgi.py

REM You should set these environment variables before running in production
REM set SECRET_KEY=your-secret-key
REM set JWT_SECRET_KEY=your-jwt-secret-key
REM set DATABASE_URL=sqlite:///pickleball.db

REM Start Waitress server
python -m waitress --port=8000 --host=0.0.0.0 wsgi:app

pause 
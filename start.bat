@echo off
echo Starting Pickleball Application...

REM Check if venv exists
if not exist venv\ (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

REM Ensure instance directory exists
if not exist instance\ (
    echo Creating instance directory...
    mkdir instance
)

REM Initialize database if it doesn't exist
if not exist instance\pickleball.db (
    echo Initializing database...
    python init_db.py
)

REM Set environment variables - no need to set DATABASE_URL as it's handled in the scripts
set FLASK_APP=app
set FLASK_ENV=development

echo.
echo Starting Flask application...
echo.

REM Run the application
python run.py

REM If there's an error, pause to see it
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with error code %ERRORLEVEL%
    pause
) 
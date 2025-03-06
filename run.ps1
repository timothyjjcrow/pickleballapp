# PowerShell script to run the Flask application

# Check if virtual environment exists and activate if it does
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..."
    & .\venv\Scripts\Activate.ps1
}

# Check if instance directory exists
if (-not (Test-Path "instance")) {
    Write-Host "Creating instance directory..."
    New-Item -ItemType Directory -Path "instance" | Out-Null
}

# Set environment variables
$env:FLASK_APP = "app"
$env:FLASK_ENV = "development"
$env:DATABASE_URL = "sqlite:///instance/app.db"

# Copy pickleball.db to app.db if needed
$pickleballDb = "instance\pickleball.db" 
$appDb = "instance\app.db"
if (Test-Path $pickleballDb) {
    if (-not (Test-Path $appDb)) {
        Write-Host "Copying pickleball.db to app.db..."
        Copy-Item $pickleballDb $appDb
    }
}

# Run the application
Write-Host "Starting Flask application..."
Write-Host "Database URL: $env:DATABASE_URL"
Write-Host "Database exists: $(Test-Path $appDb)"
python run_app.py 
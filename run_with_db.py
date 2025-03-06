import os
import shutil
from app import create_app

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///app.db'
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

# Copy pickleball.db to app.db if it exists
if os.path.exists('instance/pickleball.db'):
    shutil.copy2('instance/pickleball.db', 'instance/app.db')
    print("Copied pickleball.db to app.db")

# Create the Flask app
app = create_app()

# Run the app
if __name__ == '__main__':
    print(f"Using database: {os.environ['DATABASE_URL']}")
    print(f"Database file exists: {os.path.exists('instance/app.db')}")
    app.run(host="0.0.0.0", port=5000, debug=True) 
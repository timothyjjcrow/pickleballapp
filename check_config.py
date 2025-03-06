import os
from app import create_app

# Create the Flask app
app = create_app()

# Print configuration
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Instance path: {app.instance_path}")
print(f"Database file exists: {os.path.exists(app.instance_path + '/pickleball.db')}")
print(f"App.db file exists: {os.path.exists(app.instance_path + '/app.db')}") 
#!/usr/bin/env python
"""
Script to migrate courts data from courts.json to the database.
This is a one-time script to be run during setup.
"""

import os
import sys
import json
import logging
import importlib.util

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables directly
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'your_secret_key'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pickleball.db'
os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
os.environ['CORS_ORIGINS'] = 'http://localhost:5000'
os.environ['SOCKET_HOST'] = 'localhost'
os.environ['SOCKET_PORT'] = '5001'

# Patch the load_dotenv function to do nothing
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: None

from app import create_app, db
from app.models.court import Court
from app.services.elasticsearch import create_indices, index_court

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_courts():
    """Migrate courts data from JSON file to database."""
    app = create_app('development')
    
    # Set the database URI directly in the app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        # Load courts data from JSON file
        try:
            with open('courts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                courts_data = data.get('courts', [])
        except UnicodeDecodeError:
            try:
                with open('courts.json', 'r', encoding='latin-1') as f:
                    data = json.load(f)
                    courts_data = data.get('courts', [])
            except Exception as e:
                print(f"Error loading courts.json: {e}")
                courts_data = []
        
        # Create sample court data if no courts were loaded
        if not courts_data:
            courts_data = [
                {
                    "id": "sample-court-1",
                    "placeId": "SampleCourt1",
                    "name": "Sample Court 1",
                    "address": "123 Main St, Anytown, CA 12345, USA",
                    "phone": "555-123-4567",
                    "website": "https://samplecourt1.com",
                    "location": {
                        "lat": 37.7749,
                        "lng": -122.4194
                    },
                    "rating": 4.5,
                    "totalRatings": 25,
                    "courtType": "outdoor",
                    "surfaceType": "concrete",
                    "numberOfCourts": 4
                },
                {
                    "id": "sample-court-2",
                    "placeId": "SampleCourt2",
                    "name": "Sample Court 2",
                    "address": "456 Oak Ave, Somewhere, NY 67890, USA",
                    "phone": "555-987-6543",
                    "website": "https://samplecourt2.com",
                    "location": {
                        "lat": 40.7128,
                        "lng": -74.0060
                    },
                    "rating": 4.2,
                    "totalRatings": 18,
                    "courtType": "indoor",
                    "surfaceType": "wood",
                    "numberOfCourts": 2
                }
            ]
            print("Using sample court data since courts.json could not be loaded.")
        
        # Clear existing courts
        Court.query.delete()
        db.session.commit()
        
        # Create Elasticsearch indices
        try:
            create_indices()
            print("Elasticsearch indices created successfully!")
        except Exception as e:
            print(f"Error creating Elasticsearch indices: {e}")
        
        # Create new courts
        for court_data in courts_data:
            # Extract location data
            location = court_data.get('location', {})
            lat = location.get('lat', 0.0)
            lng = location.get('lng', 0.0)
            
            court = Court(
                uuid=court_data.get('id', ''),
                name=court_data.get('name', ''),
                place_id=court_data.get('placeId', ''),
                address=court_data.get('address', ''),
                phone=court_data.get('phone', ''),
                website=court_data.get('website', ''),
                lat=lat,
                lng=lng,
                rating=court_data.get('rating', 0.0),
                total_ratings=court_data.get('totalRatings', 0),
                hours=court_data.get('hours', {}),
                photos=court_data.get('photos', []),
                court_type=court_data.get('courtType', ''),
                surface_type=court_data.get('surfaceType', ''),
                amenities=court_data.get('amenities', []),
                number_of_courts=court_data.get('numberOfCourts', 0),
                reviews=court_data.get('reviews', [])
            )
            db.session.add(court)
        
        db.session.commit()
        
        # Index courts in Elasticsearch
        try:
            for court in Court.query.all():
                index_court(court)
            print("Courts indexed in Elasticsearch successfully!")
        except Exception as e:
            print(f"Error indexing courts in Elasticsearch: {e}")
        
        print(f"Successfully migrated {len(courts_data)} courts to the database!")

if __name__ == '__main__':
    migrate_courts() 
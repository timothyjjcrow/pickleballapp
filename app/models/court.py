from datetime import datetime
import json
from app import db

class Court(db.Model):
    """Court model for storing pickleball court details"""
    __tablename__ = 'courts'

    court_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)  # Original ID from courts.json
    place_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    total_ratings = db.Column(db.Integer, nullable=True)
    hours = db.Column(db.Text, nullable=True)  # JSON string of operating hours
    photos = db.Column(db.Text, nullable=True)  # JSON string of photo URLs
    court_type = db.Column(db.String(50), nullable=True)  # indoor, outdoor, etc.
    surface_type = db.Column(db.String(50), nullable=True)  # gym floor, concrete, etc.
    amenities = db.Column(db.Text, nullable=True)  # JSON string of amenities
    number_of_courts = db.Column(db.Integer, nullable=True)
    reviews = db.Column(db.Text, nullable=True)  # JSON string of reviews
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    games = db.relationship('Game', backref='court', lazy=True)
    
    def __init__(self, uuid, name, place_id=None, address=None, phone=None, website=None, 
                 lat=None, lng=None, rating=None, total_ratings=None, hours=None, 
                 photos=None, court_type=None, surface_type=None, amenities=None,
                 number_of_courts=None, reviews=None):
        self.uuid = uuid
        self.place_id = place_id
        self.name = name
        self.address = address
        self.phone = phone
        self.website = website
        self.lat = lat
        self.lng = lng
        self.rating = rating
        self.total_ratings = total_ratings
        self.hours = json.dumps(hours) if hours else None
        self.photos = json.dumps(photos) if photos else None
        self.court_type = court_type
        self.surface_type = surface_type
        self.amenities = json.dumps(amenities) if amenities else None
        self.number_of_courts = number_of_courts
        self.reviews = json.dumps(reviews) if reviews else None
    
    def to_dict(self):
        """Convert court object to dictionary"""
        return {
            'court_id': self.court_id,
            'uuid': self.uuid,
            'place_id': self.place_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'location': {
                'lat': self.lat,
                'lng': self.lng
            } if self.lat and self.lng else None,
            'rating': self.rating,
            'total_ratings': self.total_ratings,
            'hours': json.loads(self.hours) if self.hours else None,
            'photos': json.loads(self.photos) if self.photos else None,
            'court_type': self.court_type,
            'surface_type': self.surface_type,
            'amenities': json.loads(self.amenities) if self.amenities else None,
            'number_of_courts': self.number_of_courts,
            'reviews': json.loads(self.reviews) if self.reviews else None
        }
    
    def __repr__(self):
        return f'<Court {self.name}>' 
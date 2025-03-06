#!/usr/bin/env python
"""
Script to seed the database with sample data.
This creates sample users, courts, games, and chat messages.
"""

import os
import sys
import json
from datetime import datetime, date, time, timedelta
import bcrypt
import random

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables directly
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['SECRET_KEY'] = 'your_secret_key'
os.environ['DATABASE_URL'] = 'sqlite:///pickleball.db'
os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
os.environ['CORS_ORIGINS'] = 'http://localhost:5000'
os.environ['SOCKET_HOST'] = 'localhost'
os.environ['SOCKET_PORT'] = '5001'

# Patch the load_dotenv function to do nothing
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: None

from app import create_app, db
from app.models.user import User
from app.models.court import Court
from app.models.game import Game, GameParticipant
from app.models.chat import ChatMessage

def seed_db():
    """Seed the database with sample data."""
    app = create_app('development')
    
    # Set the database URI directly in the app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Clear existing data
        ChatMessage.query.delete()
        GameParticipant.query.delete()
        Game.query.delete()
        Court.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create sample users
        users = [
            User(username='john_doe', email='john@example.com', password='password123'),
            User(username='jane_smith', email='jane@example.com', password='password123'),
            User(username='mike_johnson', email='mike@example.com', password='password123'),
            User(username='sarah_williams', email='sarah@example.com', password='password123'),
            User(username='david_brown', email='david@example.com', password='password123')
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} sample users")
        
        # Load courts from courts.json
        courts_data = []
        try:
            with open('courts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                courts_data = data.get('courts', [])
                print(f"Successfully loaded {len(courts_data)} courts from courts.json")
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error loading courts.json: {e}")
            try:
                with open('courts.json', 'r', encoding='latin-1') as f:
                    data = json.load(f)
                    courts_data = data.get('courts', [])
                    print(f"Successfully loaded {len(courts_data)} courts from courts.json using latin-1 encoding")
            except Exception as e:
                print(f"Failed to load courts.json with latin-1 encoding: {e}")
                courts_data = []
        
        # Create courts from the loaded data
        courts = []
        for court_data in courts_data[:20]:  # Limit to first 20 courts for efficiency
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
                hours=json.dumps(court_data.get('hours', [])),
                photos=json.dumps(court_data.get('photos', [])),
                court_type=court_data.get('courtType', ''),
                surface_type=court_data.get('surfaceType', ''),
                amenities=json.dumps(court_data.get('amenities', [])),
                number_of_courts=court_data.get('numberOfCourts', 0),
                reviews=json.dumps(court_data.get('reviews', []))
            )
            db.session.add(court)
            courts.append(court)
        
        # If no courts were loaded, create some fallback sample courts
        if not courts:
            print("No courts loaded from courts.json, creating fallback sample courts")
            fallback_courts = [
                Court(
                    uuid='court-1',
                    name='Downtown Pickleball Center',
                    place_id='DowntownPB1',
                    address='123 Main St, Anytown, CA 12345, USA',
                    phone='555-123-4567',
                    website='https://downtownpickleball.com',
                    lat=37.7749,
                    lng=-122.4194,
                    rating=4.7,
                    total_ratings=42,
                    hours=json.dumps({
                        'Monday': '8:00 AM - 9:00 PM',
                        'Tuesday': '8:00 AM - 9:00 PM',
                        'Wednesday': '8:00 AM - 9:00 PM',
                        'Thursday': '8:00 AM - 9:00 PM',
                        'Friday': '8:00 AM - 10:00 PM',
                        'Saturday': '7:00 AM - 10:00 PM',
                        'Sunday': '7:00 AM - 8:00 PM'
                    }),
                    photos=json.dumps(['photo1.jpg', 'photo2.jpg']),
                    court_type='outdoor',
                    surface_type='concrete',
                    amenities=json.dumps(['restrooms', 'water fountains', 'pro shop', 'lighting']),
                    number_of_courts=8,
                    reviews=json.dumps([
                        {'user': 'PickleFan', 'rating': 5, 'comment': 'Great courts, well maintained!'},
                        {'user': 'PBNewbie', 'rating': 4, 'comment': 'Good place to learn, friendly people.'}
                    ])
                ),
                Court(
                    uuid='court-2',
                    name='Eastside Recreation Center',
                    place_id='EastsideRec1',
                    address='456 Oak Ave, Somewhere, NY 67890, USA',
                    phone='555-987-6543',
                    website='https://eastsiderec.com',
                    lat=40.7128,
                    lng=-74.0060,
                    rating=4.2,
                    total_ratings=28,
                    hours=json.dumps({
                        'Monday': '9:00 AM - 8:00 PM',
                        'Tuesday': '9:00 AM - 8:00 PM',
                        'Wednesday': '9:00 AM - 8:00 PM',
                        'Thursday': '9:00 AM - 8:00 PM',
                        'Friday': '9:00 AM - 9:00 PM',
                        'Saturday': '8:00 AM - 9:00 PM',
                        'Sunday': '8:00 AM - 7:00 PM'
                    }),
                    photos=json.dumps(['photo3.jpg', 'photo4.jpg']),
                    court_type='indoor',
                    surface_type='wood',
                    amenities=json.dumps(['restrooms', 'locker rooms', 'snack bar']),
                    number_of_courts=4,
                    reviews=json.dumps([
                        {'user': 'IndoorPlayer', 'rating': 5, 'comment': 'Best indoor courts in the area!'},
                        {'user': 'WeekendWarrior', 'rating': 3, 'comment': 'Gets crowded on weekends.'}
                    ])
                ),
                Court(
                    uuid='court-3',
                    name='Westside Community Park',
                    place_id='WestsidePark1',
                    address='789 Pine Rd, Elsewhere, TX 54321, USA',
                    phone='555-456-7890',
                    website='https://westsidepark.com',
                    lat=29.7604,
                    lng=-95.3698,
                    rating=4.0,
                    total_ratings=15,
                    hours=json.dumps({
                        'Monday': '7:00 AM - 10:00 PM',
                        'Tuesday': '7:00 AM - 10:00 PM',
                        'Wednesday': '7:00 AM - 10:00 PM',
                        'Thursday': '7:00 AM - 10:00 PM',
                        'Friday': '7:00 AM - 10:00 PM',
                        'Saturday': '7:00 AM - 10:00 PM',
                        'Sunday': '7:00 AM - 10:00 PM'
                    }),
                    photos=json.dumps(['photo5.jpg']),
                    court_type='outdoor',
                    surface_type='asphalt',
                    amenities=json.dumps(['restrooms', 'water fountains', 'shade structures']),
                    number_of_courts=6,
                    reviews=json.dumps([
                        {'user': 'ParkPlayer', 'rating': 4, 'comment': 'Nice public courts, free to use!'}
                    ])
                )
            ]
            for court in fallback_courts:
                db.session.add(court)
            courts = fallback_courts
        
        db.session.commit()
        print(f"Created {len(courts)} courts")
        
        # Select a few random courts for the games
        selected_courts = random.sample(courts, min(3, len(courts)))
        if len(selected_courts) < 3:
            # If we don't have enough courts, repeat some
            while len(selected_courts) < 3:
                selected_courts.append(selected_courts[0])
                
        # Create sample games
        today = date.today()
        games = [
            # Game 1 - Today at 10 AM
            Game(
                court_id=selected_courts[0].court_id,
                creator_id=users[0].user_id,
                date=today,
                time=time(10, 0),  # 10:00 AM
                max_players=4,
                skill_level='intermediate',
                notes='Looking for intermediate players for a fun morning game!'
            ),
            # Game 2 - Tomorrow at 2 PM
            Game(
                court_id=selected_courts[1].court_id,
                creator_id=users[1].user_id,
                date=today + timedelta(days=1),
                time=time(14, 0),  # 2:00 PM
                max_players=4,
                skill_level='beginner',
                notes='Beginner-friendly game, all welcome!'
            ),
            # Game 3 - Day after tomorrow at 6 PM
            Game(
                court_id=selected_courts[2].court_id,
                creator_id=users[2].user_id,
                date=today + timedelta(days=2),
                time=time(18, 0),  # 6:00 PM
                max_players=4,
                skill_level='advanced',
                notes='Looking for competitive players for an evening game.'
            ),
            # Game 4 - Next week
            Game(
                court_id=selected_courts[0].court_id,
                creator_id=users[3].user_id,
                date=today + timedelta(days=7),
                time=time(16, 0),  # 4:00 PM
                max_players=4,
                skill_level='intermediate',
                notes='Planning ahead for next week!'
            )
        ]
        
        for game in games:
            db.session.add(game)
        
        db.session.commit()
        print(f"Created {len(games)} sample games")
        
        # Add participants to games
        # Game 1: Creator (user 0) + users 1 and 2
        participants = [
            # Game 1 participants
            GameParticipant(game_id=games[0].game_id, user_id=users[0].user_id),  # Creator
            GameParticipant(game_id=games[0].game_id, user_id=users[1].user_id),
            GameParticipant(game_id=games[0].game_id, user_id=users[2].user_id),
            
            # Game 2 participants
            GameParticipant(game_id=games[1].game_id, user_id=users[1].user_id),  # Creator
            GameParticipant(game_id=games[1].game_id, user_id=users[3].user_id),
            
            # Game 3 participants
            GameParticipant(game_id=games[2].game_id, user_id=users[2].user_id),  # Creator
            GameParticipant(game_id=games[2].game_id, user_id=users[0].user_id),
            GameParticipant(game_id=games[2].game_id, user_id=users[4].user_id),
            
            # Game 4 participants
            GameParticipant(game_id=games[3].game_id, user_id=users[3].user_id),  # Creator
        ]
        
        for participant in participants:
            db.session.add(participant)
        
        db.session.commit()
        print(f"Added {len(participants)} participants to games")
        
        # Add chat messages to games
        messages = [
            # Messages for Game 1
            ChatMessage(
                game_id=games[0].game_id,
                user_id=users[0].user_id,
                message_text="Hi everyone! Looking forward to our game today."
            ),
            ChatMessage(
                game_id=games[0].game_id,
                user_id=users[1].user_id,
                message_text="Me too! Should I bring extra balls?"
            ),
            ChatMessage(
                game_id=games[0].game_id,
                user_id=users[0].user_id,
                message_text="Yes please, that would be great!"
            ),
            
            # Messages for Game 2
            ChatMessage(
                game_id=games[1].game_id,
                user_id=users[1].user_id,
                message_text="Welcome to the beginner's game! Don't worry about skill level, we're here to have fun."
            ),
            ChatMessage(
                game_id=games[1].game_id,
                user_id=users[3].user_id,
                message_text="Thanks for organizing this! I'm excited to learn."
            ),
            
            # Messages for Game 3
            ChatMessage(
                game_id=games[2].game_id,
                user_id=users[2].user_id,
                message_text="This is going to be a competitive one! Bring your A-game."
            ),
            ChatMessage(
                game_id=games[2].game_id,
                user_id=users[0].user_id,
                message_text="Ready for the challenge! See you all there."
            )
        ]
        
        for message in messages:
            db.session.add(message)
        
        db.session.commit()
        print(f"Added {len(messages)} chat messages")
        
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_db() 
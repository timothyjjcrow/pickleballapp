import os
from datetime import datetime, time, date
from app import create_app, db
from app.models.user import User
from app.models.court import Court
from app.models.game import Game, GameParticipant
from app.models.chat import ChatMessage

def test_models():
    """Test database models to ensure they are working correctly"""
    # Create app with test config
    app = create_app('testing')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("Testing database models...")
        
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        db.session.add(user)
        db.session.commit()
        print(f"Created user: {user}")
        
        # Create test court
        court = Court(
            uuid='test-court-123',
            name='Test Court',
            address='123 Test Ave, Testville',
            lat=40.7128,
            lng=-74.0060
        )
        db.session.add(court)
        db.session.commit()
        print(f"Created court: {court}")
        
        # Create test game
        game = Game(
            court_id=court.court_id,
            creator_id=user.user_id,
            date=date.today(),
            time=time(14, 0),  # 2:00 PM
            max_players=4,
            skill_level='intermediate',
            notes='Test game'
        )
        db.session.add(game)
        db.session.commit()
        print(f"Created game: {game}")
        
        # Add creator as participant
        participant = GameParticipant(
            game_id=game.game_id,
            user_id=user.user_id
        )
        db.session.add(participant)
        db.session.commit()
        print(f"Added participant: {participant}")
        
        # Add a chat message
        message = ChatMessage(
            game_id=game.game_id,
            user_id=user.user_id,
            message_text="Hello, this is a test message!"
        )
        db.session.add(message)
        db.session.commit()
        print(f"Added chat message: {message}")
        
        # Test retrieving game with its court
        game_with_court = Game.query.filter_by(game_id=game.game_id).first()
        if game_with_court and game_with_court.court:
            print(f"Game is associated with court: {game_with_court.court.name}")
        else:
            print("ERROR: Game is not associated with a court")
        
        # Test retrieving court with its games
        court_with_games = Court.query.filter_by(court_id=court.court_id).first()
        if court_with_games and court_with_games.games:
            print(f"Court has {len(court_with_games.games)} games")
        else:
            print("ERROR: Court has no games")
        
        # Test retrieving game with its participants
        game_with_participants = Game.query.filter_by(game_id=game.game_id).first()
        if game_with_participants and game_with_participants.participants:
            print(f"Game has {len(game_with_participants.participants)} participants")
        else:
            print("ERROR: Game has no participants")
        
        # Test retrieving game with its chat messages
        game_with_messages = Game.query.filter_by(game_id=game.game_id).first()
        if game_with_messages and game_with_messages.messages:
            print(f"Game has {len(game_with_messages.messages)} chat messages")
        else:
            print("ERROR: Game has no chat messages")
        
        # Test status filtering on Game model
        games_with_status = Game.query.filter_by(status='scheduled').all()
        print(f"Found {len(games_with_status)} scheduled games")
        
        print("All tests completed successfully!")
        
        # Clean up test data
        db.session.delete(message)
        db.session.delete(participant)
        db.session.delete(game)
        db.session.delete(court)
        db.session.delete(user)
        db.session.commit()

if __name__ == "__main__":
    test_models() 
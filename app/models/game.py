from datetime import datetime
from app import db

class Game(db.Model):
    """Game model for scheduling pickleball games"""
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.court_id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    max_players = db.Column(db.Integer, default=4)
    skill_level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced
    status = db.Column(db.String(20), default='scheduled')  # scheduled, cancelled, completed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = db.relationship('GameParticipant', backref='game', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, court_id, creator_id, date, time, max_players=4, skill_level=None, notes=None):
        self.court_id = court_id
        self.creator_id = creator_id
        self.date = date
        self.time = time
        self.max_players = max_players
        self.skill_level = skill_level
        self.notes = notes
    
    def to_dict(self, include_participants=True):
        """Convert game object to dictionary"""
        game_dict = {
            'game_id': self.game_id,
            'court_id': self.court_id,
            'creator_id': self.creator_id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'max_players': self.max_players,
            'skill_level': self.skill_level,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_time': f"{self.date.isoformat()}T{self.time.isoformat()}" if self.date and self.time else None
        }
        
        if include_participants:
            game_dict['participants'] = [p.to_dict(include_game=False) for p in self.participants]
            # Also add a players field for compatibility with the frontend
            game_dict['players'] = game_dict['participants']
        
        return game_dict
    
    def __repr__(self):
        return f'<Game {self.game_id} on {self.date} at {self.time}>'


class GameParticipant(db.Model):
    """Model for tracking participants in a game"""
    __tablename__ = 'game_participants'

    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, game_id, user_id):
        self.game_id = game_id
        self.user_id = user_id
    
    def to_dict(self, include_game=True):
        """Convert game participant object to dictionary"""
        participant_dict = {
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
        
        if include_game:
            participant_dict['game_id'] = self.game_id
        
        return participant_dict
    
    def __repr__(self):
        return f'<GameParticipant game_id={self.game_id}, user_id={self.user_id}>' 
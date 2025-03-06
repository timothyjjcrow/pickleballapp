from datetime import datetime
from app import db

class ChatMessage(db.Model):
    """Chat message model for game-specific chat"""
    __tablename__ = 'chat_messages'

    message_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, game_id, user_id, message_text):
        self.game_id = game_id
        self.user_id = user_id
        self.message_text = message_text
    
    def to_dict(self, include_user=True):
        """Convert chat message object to dictionary"""
        message_dict = {
            'message_id': self.message_id,
            'game_id': self.game_id,
            'user_id': self.user_id,
            'message_text': self.message_text,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
        
        if include_user and self.user:
            message_dict['username'] = self.user.username
        
        return message_dict
    
    def __repr__(self):
        return f'<ChatMessage {self.message_id} by user {self.user_id}>' 
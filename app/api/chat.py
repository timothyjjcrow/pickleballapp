from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.chat import ChatMessage
from app.models.game import Game, GameParticipant

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/games/<int:game_id>', methods=['GET'])
@jwt_required()
def get_chat_messages(game_id):
    """Retrieve chat messages for a game"""
    current_user_id = get_jwt_identity()
    
    # Check if game exists
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    
    # Check if user is a participant
    participant = GameParticipant.query.filter_by(
        game_id=game_id, 
        user_id=current_user_id
    ).first()
    
    if not participant:
        return jsonify({'message': 'You are not a participant in this game'}), 403
    
    # Get messages
    messages = ChatMessage.query.filter_by(game_id=game_id).order_by(ChatMessage.timestamp).all()
    
    return jsonify({
        'messages': [message.to_dict() for message in messages]
    }), 200

@chat_bp.route('/games/<int:game_id>', methods=['POST'])
@jwt_required()
def send_chat_message(game_id):
    """Send a message to a game's chat"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('message'):
        return jsonify({'message': 'Missing message content'}), 400
    
    # Check if game exists
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    
    # Check if user is a participant
    participant = GameParticipant.query.filter_by(
        game_id=game_id, 
        user_id=current_user_id
    ).first()
    
    if not participant:
        return jsonify({'message': 'You are not a participant in this game'}), 403
    
    try:
        # Create new message
        message = ChatMessage(
            game_id=game_id,
            user_id=current_user_id,
            message_text=data['message']
        )
        db.session.add(message)
        db.session.commit()
        
        # In a real application, we would also broadcast this message via WebSockets
        
        return jsonify({
            'message': 'Message sent successfully',
            'chat_message': message.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error sending message: {str(e)}'}), 500 
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.game import Game, GameParticipant
from app.models.user import User
from app.models.court import Court

games_bp = Blueprint('games', __name__)

@games_bp.route('', methods=['POST'])
@jwt_required()
def create_game():
    """Schedule a new game"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Debug - log received data
    print(f"Received game data: {data}")
    
    # Validate input
    if not data:
        return jsonify({'message': 'No data provided'}), 400
        
    # Check for required fields
    required_fields = ['court_id', 'date', 'time']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Check if court exists
    court = Court.query.get(data['court_id'])
    if not court:
        return jsonify({'message': f'Court not found with ID: {data["court_id"]}'}), 404
    
    try:
        # Parse date and time
        try:
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 422
            
        try:
            time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'message': 'Invalid time format. Use HH:MM (24-hour format)'}), 422
        
        # Create new game
        game = Game(
            court_id=data['court_id'],
            creator_id=current_user_id,
            date=date,
            time=time,
            max_players=data.get('max_players', 4),
            skill_level=data.get('skill_level'),
            notes=data.get('notes')
        )
        db.session.add(game)
        # Flush the session to get the game_id
        db.session.flush()
        
        # Add creator as a participant
        participant = GameParticipant(
            game_id=game.game_id,
            user_id=current_user_id
        )
        db.session.add(participant)
        
        db.session.commit()
        
        # Index in Elasticsearch (to be implemented in search service)
        
        return jsonify({
            'message': 'Game scheduled successfully',
            'game_id': game.game_id,
            'game': game.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'message': f'Invalid date or time format: {str(e)}'}), 422
    except Exception as e:
        db.session.rollback()
        print(f"Error creating game: {str(e)}")
        return jsonify({'message': f'Error scheduling game: {str(e)}'}), 500

@games_bp.route('', methods=['GET'])
def get_games():
    """List scheduled games with optional filters"""
    # Get query parameters
    court_id = request.args.get('court_id', type=int)
    date = request.args.get('date')
    status = request.args.get('status', 'scheduled')
    
    # Build query
    query = Game.query.join(Game.court)
    
    if court_id:
        query = query.filter(Game.court_id == court_id)
    
    if date:
        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(Game.date == filter_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if status:
        query = query.filter(Game.status == status)
    
    # Execute query
    games = query.order_by(Game.date, Game.time).all()
    
    # Transform the results to include court information
    game_list = []
    for game in games:
        game_data = game.to_dict()
        game_data['court'] = game.court.to_dict() if game.court else None
        game_data['scheduled_time'] = f"{game.date.isoformat()}T{game.time.isoformat()}" if game.date and game.time else None
        game_data['players'] = game_data['participants']
        game_list.append(game_data)
    
    return jsonify({
        'games': game_list
    }), 200

@games_bp.route('/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get details of a specific game"""
    game = Game.query.join(Game.court).filter(Game.game_id == game_id).first()
    
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    
    # Transform the result to include court information
    game_data = game.to_dict()
    game_data['court'] = game.court.to_dict() if game.court else None
    game_data['scheduled_time'] = f"{game.date.isoformat()}T{game.time.isoformat()}" if game.date and game.time else None
    game_data['players'] = game_data['participants']
    
    return jsonify({
        'game': game_data
    }), 200

@games_bp.route('/<int:game_id>/join', methods=['POST'])
@jwt_required()
def join_game(game_id):
    """Join a game"""
    current_user_id = get_jwt_identity()
    
    # Check if game exists
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    
    # Check if game is full
    if len(game.participants) >= game.max_players:
        return jsonify({'message': 'Game is already full'}), 400
    
    # Check if user is already a participant
    existing_participant = GameParticipant.query.filter_by(
        game_id=game_id, 
        user_id=current_user_id
    ).first()
    
    if existing_participant:
        return jsonify({'message': 'You are already a participant in this game'}), 400
    
    try:
        # Add user as a participant
        participant = GameParticipant(
            game_id=game_id,
            user_id=current_user_id
        )
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully joined the game',
            'game': game.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error joining game: {str(e)}'}), 500

@games_bp.route('/<int:game_id>/leave', methods=['POST'])
@jwt_required()
def leave_game(game_id):
    """Leave a game"""
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
        return jsonify({'message': 'You are not a participant in this game'}), 400
    
    try:
        # Remove user from participants
        db.session.delete(participant)
        
        # If the user is the creator and there are other participants,
        # transfer ownership to the next participant
        if game.creator_id == current_user_id and len(game.participants) > 1:
            # Find another participant who is not the current user
            for p in game.participants:
                if p.user_id != current_user_id:
                    game.creator_id = p.user_id
                    break
        
        # If no participants left, cancel the game
        if len(game.participants) <= 1:  # Only the current user is left
            game.status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully left the game'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error leaving game: {str(e)}'}), 500 
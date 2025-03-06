from flask import Blueprint, request, jsonify, current_app
from elasticsearch import Elasticsearch
from app.models.court import Court
from app.models.game import Game
from app.services.elasticsearch import get_elasticsearch_client
import math

search_bp = Blueprint('search', __name__)

# Function to calculate distance between two coordinate points
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers
    r = 6371
    return c * r

@search_bp.route('/courts', methods=['GET'])
def search_courts():
    """Search for courts using Elasticsearch or by location radius"""
    query = request.args.get('q', '')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = request.args.get('radius', 10)  # Default radius: 10km
    
    # Location-based search has priority
    if lat and lng:
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            # Query all courts that have coordinates
            all_courts = Court.query.filter(Court.lat.isnot(None), Court.lng.isnot(None)).all()
            
            # Filter courts by distance
            courts_with_distance = []
            for court in all_courts:
                distance = calculate_distance(lat, lng, court.lat, court.lng)
                if distance <= radius:
                    court_dict = court.to_dict()
                    court_dict['distance'] = round(distance, 2)  # Add distance to court data
                    courts_with_distance.append(court_dict)
            
            # Sort by distance
            courts_with_distance.sort(key=lambda x: x['distance'])
            
            return jsonify({
                'courts': courts_with_distance,
                'search_method': 'location_radius',
                'params': {
                    'lat': lat,
                    'lng': lng,
                    'radius': radius
                }
            }), 200
        except (ValueError, TypeError) as e:
            return jsonify({'message': f'Invalid location parameters: {str(e)}'}), 400
    
    # Text-based search if no location data provided
    if not query:
        return jsonify({'message': 'Search query is required for text search'}), 400
    
    es = get_elasticsearch_client()
    if not es:
        # Fallback to database search if Elasticsearch is not configured
        courts = Court.query.filter(Court.name.ilike(f'%{query}%')).all()
        return jsonify({
            'courts': [court.to_dict() for court in courts],
            'search_method': 'database'
        }), 200
    
    try:
        # Search in Elasticsearch
        index = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
        response = es.search(
            index=f"{index}_courts",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "address", "court_type", "surface_type", "amenities"]
                    }
                }
            }
        )
        
        # Extract results
        hits = response['hits']['hits']
        court_ids = [hit['_source']['court_id'] for hit in hits]
        
        # Get courts from database
        courts = Court.query.filter(Court.court_id.in_(court_ids)).all()
        
        # Sort courts to match Elasticsearch ranking
        sorted_courts = []
        for court_id in court_ids:
            for court in courts:
                if court.court_id == court_id:
                    sorted_courts.append(court)
                    break
        
        return jsonify({
            'courts': [court.to_dict() for court in sorted_courts],
            'search_method': 'elasticsearch'
        }), 200
    
    except Exception as e:
        # Fallback to database search if Elasticsearch query fails
        courts = Court.query.filter(Court.name.ilike(f'%{query}%')).all()
        return jsonify({
            'courts': [court.to_dict() for court in courts],
            'search_method': 'database',
            'error': str(e)
        }), 200

@search_bp.route('/games', methods=['GET'])
def search_games():
    """Search for games using Elasticsearch or by location radius"""
    query = request.args.get('q', '')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = request.args.get('radius', 10)  # Default radius: 10km
    
    # Location-based search has priority
    if lat and lng:
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            # Get all games and their courts with coordinates
            games = Game.query.join(Court).filter(Court.lat.isnot(None), Court.lng.isnot(None)).all()
            
            # Filter games by court distance
            games_with_distance = []
            for game in games:
                court = game.court
                distance = calculate_distance(lat, lng, court.lat, court.lng)
                if distance <= radius:
                    game_dict = game.to_dict()
                    game_dict['distance'] = round(distance, 2)  # Add distance to game data
                    game_dict['court_location'] = {
                        'lat': court.lat,
                        'lng': court.lng
                    }
                    games_with_distance.append(game_dict)
            
            # Sort by distance
            games_with_distance.sort(key=lambda x: x['distance'])
            
            return jsonify({
                'games': games_with_distance,
                'search_method': 'location_radius',
                'params': {
                    'lat': lat,
                    'lng': lng,
                    'radius': radius
                }
            }), 200
        except (ValueError, TypeError) as e:
            return jsonify({'message': f'Invalid location parameters: {str(e)}'}), 400
    
    # Text-based search if no location data provided
    if not query:
        return jsonify({'message': 'Search query is required for text search'}), 400
    
    es = get_elasticsearch_client()
    if not es:
        # Fallback to database search if Elasticsearch is not configured
        games = Game.query.join(Court).filter(
            (Game.skill_level.ilike(f'%{query}%')) | 
            (Game.notes.ilike(f'%{query}%')) | 
            (Court.name.ilike(f'%{query}%'))
        ).all()
        return jsonify({
            'games': [game.to_dict() for game in games],
            'search_method': 'database',
            'message': 'Elasticsearch not available, using database search'
        }), 200
    
    try:
        # Search in Elasticsearch
        index = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
        response = es.search(
            index=f"{index}_games",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["court_name^2", "skill_level", "notes", "status"]
                    }
                }
            }
        )
        
        # Extract results
        hits = response['hits']['hits']
        game_ids = [hit['_source']['game_id'] for hit in hits]
        
        # Get full game objects from database
        games = Game.query.filter(Game.game_id.in_(game_ids)).all()
        
        # Sort games to match Elasticsearch ranking
        sorted_games = []
        for game_id in game_ids:
            for game in games:
                if game.game_id == game_id:
                    sorted_games.append(game)
                    break
        
        return jsonify({
            'games': [game.to_dict() for game in sorted_games],
            'search_method': 'elasticsearch'
        }), 200
    except Exception as e:
        # Fallback to database search if Elasticsearch fails
        games = Game.query.join(Court).filter(
            (Game.skill_level.ilike(f'%{query}%')) | 
            (Game.notes.ilike(f'%{query}%')) | 
            (Court.name.ilike(f'%{query}%'))
        ).all()
        return jsonify({
            'games': [game.to_dict() for game in games],
            'search_method': 'database',
            'error': str(e),
            'message': 'Elasticsearch query failed, using database search'
        }), 200 
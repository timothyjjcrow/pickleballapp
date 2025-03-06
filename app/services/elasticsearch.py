from flask import current_app
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError
import logging

logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """Get Elasticsearch client with authentication"""
    es_url = current_app.config.get('ELASTICSEARCH_URL')
    es_username = current_app.config.get('ELASTICSEARCH_USERNAME')
    es_password = current_app.config.get('ELASTICSEARCH_PASSWORD')
    
    if not es_url:
        logger.warning("Elasticsearch URL not configured")
        return None
    
    try:
        client = Elasticsearch(
            es_url,
            basic_auth=(es_username, es_password) if es_username and es_password else None,
            verify_certs=True
        )
        # Test connection
        if not client.ping():
            logger.warning("Could not connect to Elasticsearch")
            return None
        return client
    except Exception as e:
        logger.warning(f"Error connecting to Elasticsearch: {e}")
        return None

def create_indices():
    """Create Elasticsearch indices if they don't exist"""
    es = get_elasticsearch_client()
    if not es:
        logger.warning("Elasticsearch not configured, skipping index creation")
        return False
    
    index_prefix = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
    
    # Court index
    court_index = f"{index_prefix}_courts"
    court_mapping = {
        "mappings": {
            "properties": {
                "court_id": {"type": "integer"},
                "uuid": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "english"},
                "address": {"type": "text", "analyzer": "english"},
                "court_type": {"type": "keyword"},
                "surface_type": {"type": "keyword"},
                "amenities": {"type": "text", "analyzer": "english"},
                "rating": {"type": "float"},
                "number_of_courts": {"type": "integer"}
            }
        }
    }
    
    # Game index
    game_index = f"{index_prefix}_games"
    game_mapping = {
        "mappings": {
            "properties": {
                "game_id": {"type": "integer"},
                "court_id": {"type": "integer"},
                "court_name": {"type": "text", "analyzer": "english"},
                "date": {"type": "date"},
                "time": {"type": "keyword"},
                "skill_level": {"type": "keyword"},
                "status": {"type": "keyword"},
                "notes": {"type": "text", "analyzer": "english"},
                "max_players": {"type": "integer"},
                "current_players": {"type": "integer"}
            }
        }
    }
    
    try:
        # Create court index if it doesn't exist
        if not es.indices.exists(index=court_index):
            es.indices.create(index=court_index, body=court_mapping)
            logger.info(f"Created Elasticsearch index: {court_index}")
        
        # Create game index if it doesn't exist
        if not es.indices.exists(index=game_index):
            es.indices.create(index=game_index, body=game_mapping)
            logger.info(f"Created Elasticsearch index: {game_index}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating Elasticsearch indices: {str(e)}")
        return False

def index_court(court):
    """Index a court in Elasticsearch"""
    es = get_elasticsearch_client()
    if not es:
        return False
    
    index_prefix = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
    court_index = f"{index_prefix}_courts"
    
    court_dict = court.to_dict()
    
    # Prepare document for indexing
    doc = {
        "court_id": court.court_id,
        "uuid": court.uuid,
        "name": court.name,
        "address": court.address,
        "court_type": court.court_type,
        "surface_type": court.surface_type,
        "amenities": court.amenities,  # This is a JSON string, might need parsing
        "rating": court.rating,
        "number_of_courts": court.number_of_courts
    }
    
    try:
        es.index(index=court_index, id=court.court_id, document=doc)
        logger.info(f"Indexed court {court.court_id} in Elasticsearch")
        return True
    except Exception as e:
        logger.error(f"Error indexing court {court.court_id}: {str(e)}")
        return False

def index_game(game):
    """Index a game in Elasticsearch"""
    es = get_elasticsearch_client()
    if not es:
        return False
    
    index_prefix = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
    game_index = f"{index_prefix}_games"
    
    # Get court name for better search
    court_name = game.court.name if game.court else "Unknown Court"
    
    # Prepare document for indexing
    doc = {
        "game_id": game.game_id,
        "court_id": game.court_id,
        "court_name": court_name,
        "date": game.date.isoformat() if game.date else None,
        "time": game.time.isoformat() if game.time else None,
        "skill_level": game.skill_level,
        "status": game.status,
        "notes": game.notes,
        "max_players": game.max_players,
        "current_players": len(game.participants)
    }
    
    try:
        es.index(index=game_index, id=game.game_id, document=doc)
        logger.info(f"Indexed game {game.game_id} in Elasticsearch")
        return True
    except Exception as e:
        logger.error(f"Error indexing game {game.game_id}: {str(e)}")
        return False

def delete_court_index(court_id):
    """Delete a court from Elasticsearch index"""
    es = get_elasticsearch_client()
    if not es:
        return False
    
    index_prefix = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
    court_index = f"{index_prefix}_courts"
    
    try:
        es.delete(index=court_index, id=court_id)
        logger.info(f"Deleted court {court_id} from Elasticsearch")
        return True
    except NotFoundError:
        logger.warning(f"Court {court_id} not found in Elasticsearch")
        return True  # Not an error if it doesn't exist
    except Exception as e:
        logger.error(f"Error deleting court {court_id}: {str(e)}")
        return False

def delete_game_index(game_id):
    """Delete a game from Elasticsearch index"""
    es = get_elasticsearch_client()
    if not es:
        return False
    
    index_prefix = current_app.config.get('ELASTICSEARCH_INDEX', 'pickleball_dev')
    game_index = f"{index_prefix}_games"
    
    try:
        es.delete(index=game_index, id=game_id)
        logger.info(f"Deleted game {game_id} from Elasticsearch")
        return True
    except NotFoundError:
        logger.warning(f"Game {game_id} not found in Elasticsearch")
        return True  # Not an error if it doesn't exist
    except Exception as e:
        logger.error(f"Error deleting game {game_id}: {str(e)}")
        return False 
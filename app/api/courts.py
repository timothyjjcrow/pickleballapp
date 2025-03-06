from flask import Blueprint, request, jsonify
from app.models.court import Court

courts_bp = Blueprint('courts', __name__)

@courts_bp.route('', methods=['GET'])
def get_courts():
    """List all courts with optional filters"""
    # Get query parameters
    name = request.args.get('name')
    court_type = request.args.get('court_type')
    
    # Build query
    query = Court.query
    
    if name:
        query = query.filter(Court.name.ilike(f'%{name}%'))
    
    if court_type:
        query = query.filter_by(court_type=court_type)
    
    # Execute query
    courts = query.order_by(Court.name).all()
    
    return jsonify({
        'courts': [court.to_dict() for court in courts]
    }), 200

@courts_bp.route('/<int:court_id>', methods=['GET'])
def get_court(court_id):
    """Get details of a specific court"""
    court = Court.query.get(court_id)
    
    if not court:
        return jsonify({'message': 'Court not found'}), 404
    
    # Return the court data directly, not wrapped in another object
    # This matches what the frontend loadCourtDetailsPage function expects
    return jsonify(court.to_dict()), 200 
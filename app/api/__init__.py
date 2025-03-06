# This file makes the api directory a Python package 

from flask import Blueprint, render_template

# Create a blueprint for the frontend routes
frontend_bp = Blueprint('frontend', __name__, template_folder='../templates')

@frontend_bp.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html') 
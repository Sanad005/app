# backend/app/__init__.py

from flask import Flask
from app import main  # Import all the query functions

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-change-me'
    
    # Register routes/blueprints
    from app.routes import bp  # You'll create this next
    app.register_blueprint(bp)
    
    return app
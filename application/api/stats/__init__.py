from flask import Blueprint

# Define the Blueprint for the Users module
statistics_bp = Blueprint('stats', __name__)

# Import routes after defining the Blueprint to avoid circular imports
from . import routes

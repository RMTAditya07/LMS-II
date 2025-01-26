from flask import Blueprint

# Define the Blueprint for the Users module
requests_bp = Blueprint('requests', __name__)

# Import routes after defining the Blueprint to avoid circular imports
from . import routes

from flask import Blueprint

# Create the blueprint
main_bp = Blueprint('main', __name__)

# Import routes to register them
from . import routes
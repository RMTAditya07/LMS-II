
from flask import Blueprint, redirect, request

users_bp_proxy = Blueprint('users_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v1"

# Proxy route to always forward to the latest version
@users_bp_proxy.route('/api/user/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@users_bp_proxy.route('/api/user/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/user/{endpoint}', code=307)  # Keeps HTTP method & request body
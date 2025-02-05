from flask import Blueprint, redirect, request

sections_bp_proxy = Blueprint('sections_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v2"

# Proxy route to always forward to the latest version
@sections_bp_proxy.route('/api/sections/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@sections_bp_proxy.route('/api/sections/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/sections/{endpoint}', code=307)  # Keeps HTTP method & request body
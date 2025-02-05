from flask import Blueprint, redirect, request

stats_bp_proxy = Blueprint('stats_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v1"

# Proxy route to always forward to the latest version
@stats_bp_proxy.route('/api/stats/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@stats_bp_proxy.route('/api/stats/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/stats/{endpoint}', code=307)  # Keeps HTTP method & request body
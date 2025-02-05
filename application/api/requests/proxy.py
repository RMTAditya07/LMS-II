from flask import Blueprint, redirect, request

requests_bp_proxy = Blueprint('requests_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v1"

# Proxy route to always forward to the latest version
@requests_bp_proxy.route('/api/requests/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@requests_bp_proxy.route('/api/requests/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/requests/{endpoint}', code=307)  # Keeps HTTP method & request body
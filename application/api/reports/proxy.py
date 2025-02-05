from flask import Blueprint, redirect, request

reports_bp_proxy = Blueprint('reports_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v1"

# Proxy route to always forward to the latest version
@reports_bp_proxy.route('/api/reports/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@reports_bp_proxy.route('/api/reports/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/reports/{endpoint}', code=307)  # Keeps HTTP method & request body
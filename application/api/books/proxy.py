from flask import Blueprint, redirect, request

books_bp_proxy = Blueprint('books_bp_proxy', __name__)

# Define the latest version
LATEST_VERSION = "v1"

# Proxy route to always forward to the latest version
@books_bp_proxy.route('/api/books/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@books_bp_proxy.route('/api/books/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_latest_version(endpoint):
    return redirect(f'/api/{LATEST_VERSION}/books/{endpoint}', code=307)  # Keeps HTTP method & request body
from flask import Blueprint, request, jsonify, session
from flask_security import auth_required, roles_required
from application.api.requests.services import (
    get_requests_by_status_service,
    approve_request_service,
    reject_request_service,
    revoke_request_service,
    create_book_request_service,
    get_user_book_requests_service,
    return_book_service,
)
from . import requests_bp

@auth_required("token")
@roles_required("admin")
@requests_bp.route('/status/<status>', methods=['GET'])
def get_requests_by_status(status):
    result, status_code = get_requests_by_status_service(status)
    return jsonify(result), status_code



@requests_bp.route('/approve/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    result, status_code = approve_request_service(request_id)
    return jsonify(result), status_code


@requests_bp.route('/reject/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    result, status_code = reject_request_service(request_id)
    return jsonify(result), status_code


@requests_bp.route('/revoke/<int:request_id>', methods=['POST'])
def revoke_request(request_id):
    result, status_code = revoke_request_service(request_id)
    return jsonify(result), status_code


@auth_required("token")
@roles_required("student")
@requests_bp.route('/create', methods=['POST'])
def create_book_request():
    data = request.get_json()
    result, status_code = create_book_request_service(data)
    return jsonify(result), status_code


@requests_bp.route('/user/requests', methods=['GET'])
def get_user_book_requests():
    result, status_code = get_user_book_requests_service()
    return jsonify(result), status_code


@requests_bp.route('/return/<int:book_request_id>', methods=['POST'])
def return_book(book_request_id):
    data = request.get_json()
    result, status_code = return_book_service(book_request_id, data)
    return jsonify(result), status_code


@requests_bp.route('/accepted-books', methods=['GET'])
def get_accepted_books(book_request_id):
    user_id = session.get('user_id')
    result, status_code = get_accepted_books(user_id)
    return jsonify(result), status_code


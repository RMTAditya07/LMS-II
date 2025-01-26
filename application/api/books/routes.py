from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_security import auth_required, roles_required, roles_accepted
from .services import (
    get_all_books_service,
    add_book_service,
    delete_book_service,
    download_book_service,
    view_book_service,
    get_book_service,
    update_book_service,
    get_reviews_service
)

from . import books_bp

@auth_required("token")
@roles_accepted('admin', 'student')
@books_bp.route('/', methods=['GET'])
def get_all_books():
    try:
        response, status_code = get_all_books_service(request.args)
        return jsonify(response), status_code
    except SQLAlchemyError as e:
        # Log the error
        logger.error(f"Database error: {str(e)}", exc_info=True)
        # Respond with a user-friendly message
        return jsonify({'error': 'Database failure. Please try again later.'}), 500
    except Exception as e:
        # Log the error
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Respond with a generic error message
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500


@auth_required("token")
@roles_required("admin")
@books_bp.route('/', methods=['POST'])
def add_book():
    data = request.form
    pdf_file = request.files.get('pdf_file')
    if not pdf_file:
        return jsonify({'error': 'PDF file is required'}), 400

    response, status_code = add_book_service(data, pdf_file)
    return jsonify(response), status_code

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    response, status_code = delete_book_service(book_id)
    return jsonify(response), status_code

@books_bp.route('/<int:book_id>/download', methods=['GET'])
def download_book(book_id):
    return download_book_service(book_id)

@books_bp.route('/<int:book_id>/view', methods=['GET'])
def view_book(book_id):
    return view_book_service(book_id)

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    response, status_code = get_book_service(book_id)
    return jsonify(response), status_code

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.form
    file = request.files.get('pdf_file')
    response, status_code = update_book_service(book_id, data, file)
    return jsonify(response), status_code

@books_bp.route('/<int:book_id>/reviews', methods=['GET'])
def get_reviews(book_id):
    response, status_code = get_reviews_service(book_id)
    return jsonify(response), status_code
from flask import request, jsonify, session
from .services import (
    get_statistics_service,
    get_student_statistics_service,
    get_admin_statistics_service
)

from . import statistics_bp

@statistics_bp.route('/', methods=['GET'])
def get_statistics():
    stat_type = request.args.get('type')
    try:
        data = get_statistics_service(stat_type)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@statistics_bp.route('/student', methods=['GET'])
def get_student_statistics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401
    try:
        data = get_student_statistics_service(user_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/admin', methods=['GET'])
def get_admin_statistics():
    try:
        data = get_admin_statistics_service()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch statistics'}), 500

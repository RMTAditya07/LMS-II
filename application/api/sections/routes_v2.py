from datetime import datetime
from flask import Blueprint, redirect, request, jsonify
from flask_security import auth_required, roles_required, roles_accepted
from .services import (
    get_all_sections,
    create_section,
    delete_section,
    get_section_by_id,
    update_section,
)

sections_bp_v2 = Blueprint("sections_v2", __name__)


@auth_required("token")
@roles_accepted('admin', 'student')
@sections_bp_v2.route("/", methods=["GET"])
def fetch_sections():
    sections = get_all_sections()
    return jsonify(sections), 200


@auth_required("token")
@roles_required("admin")
@sections_bp_v2.route("/", methods=["POST"])
def add_section():
    """formating the date_created in v2"""
    try:
        data = request.json
        new_section = create_section(
            name=data.get("name"), 
            description=data.get("description"),
        )
        # ✅ Convert full timestamp to YYYY-MM-DD format
        date_created = datetime.strptime(new_section.date_created, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d")

        return jsonify({
            'id': new_section.id,
            'name': new_section.name,
            'description': new_section.description,
            'date_created': date_created  # ✅ Formatted Date
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@sections_bp_v2.route("/<int:section_id>", methods=["DELETE"])
def remove_section(section_id):
    try:
        delete_section(section_id)
        return '', 204
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@sections_bp_v2.route("/<int:section_id>", methods=["GET"])
def fetch_section(section_id):
    user_id = request.headers.get('X-User-ID')  # Example of user context
    try:
        section = get_section_by_id(section_id, user_id)
        return jsonify(section), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@sections_bp_v2.route("/<int:section_id>", methods=["PUT"])
def modify_section(section_id):
    try:
        data = request.json
        updated_section = update_section(section_id, data)
        return jsonify({'id': updated_section.id, 'name': updated_section.name, 'description': updated_section.description}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

from flask import jsonify, request
from flask_login import current_user
from flask_restful import marshal, fields
from flask_security import auth_required, roles_required
from application.api.users.services import activate_instructor_by_id, fetch_all_users, fetch_user_credit_points, login_user, update_user_last_visit
from .models import User


from . import users_bp

user_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "active":fields.Boolean,
    "last_visit_date" : fields.DateTime,
    "date_joined":fields.DateTime,
    "credit_points":fields.Integer,
    "username" : fields.String,
    "name":fields.String
}


@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400
    
    result, error = login_user(email, password)
    if error:
        return jsonify({"message": error}), 404 if error == "User not found" else 400
    
    return jsonify(result)

@auth_required("token")
@roles_required("admin")
@users_bp.route('/', methods=['GET'])
def get_all_users():
    users = fetch_all_users()
    if not users:
        return jsonify({"message": "No users found"}), 404
    return jsonify(marshal(users, user_fields))


@users_bp.route('/instructor/<int:inst_id>/activate', methods=['POST'])
def activate_instructor(inst_id):
    success, error = activate_instructor_by_id(inst_id)
    if not success:
        return jsonify({"message": error}), 404
    return jsonify({"message": "Instructor activated successfully"}), 200

@auth_required()
@users_bp.route('/credit-points', methods=['GET'])
def get_user_credit_points():
    user_id = current_user.id
    credit_points, error = fetch_user_credit_points(user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({'creditPoints': credit_points})

@users_bp.route('/last-visit', methods=['PUT'])
def update_last_visit():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400
    
    success, error = update_user_last_visit(user_id)
    if not success:
        return jsonify({'message': error}), 404
    
    return jsonify({'message': 'Last visit date updated successfully'}), 200
from datetime import datetime
from application.api.users.models import User
from application.sec import datastore
from werkzeug.security import check_password_hash
from application.models import db

def login_user(email, password):
    user = datastore.find_user(email=email)
    if not user:
        return None, "User not found"
    
    if check_password_hash(user.password, password):
        return {
            "token": user.get_auth_token(),
            "email": user.email,
            "role": user.roles[0].name,
            "user_id": user.id
        }, None
    else:
        return None, "Wrong Password"
    
def fetch_all_users():
    users = User.query.all()
    if len(users) == 0:
        return None, "No users found"
    return users

def activate_instructor_by_id(inst_id):
    instructor = User.query.get(inst_id)
    if not instructor or "inst" not in [role.name for role in instructor.roles]:
        return False, "Instructor not found"
    instructor.active = True
    db.session.commit()
    return True, None

def fetch_user_credit_points(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user.credit_points, None
    else:
        return None, "User not found"
    
def update_user_last_visit(user_id):
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    
    user.last_visit_date = datetime.utcnow()
    db.session.commit()
    return True, None


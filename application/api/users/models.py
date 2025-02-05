
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Time
from flask_security import UserMixin, RoleMixin
from application.extensions import db
from sqlalchemy.orm import relationship

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    active = Column(db.Boolean(), default=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    credit_points = Column(Integer, default=100)
    last_visit_date = Column(db.DateTime, default=datetime.utcnow)
    reminder_time = Column(Time, nullable=True)

    roles = relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    book_requests = relationship("BookRequest", backref="user")


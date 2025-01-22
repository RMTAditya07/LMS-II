from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, LargeBinary, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

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

class Section(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)

    books = relationship("Book", back_populates="section")

    def get_books_count(self):
        return db.session.query(func.count(Book.id)).filter(Book.section_id == self.id).scalar() or 0

class Book(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    authors = Column(String(255))
    section_id = Column(Integer, ForeignKey("section.id"), nullable=False)
    pdf_file = Column(LargeBinary, nullable=False)  # Column to store PDF file data
    file_name = Column(String(255), nullable=False)  # Stores the uploaded PDF filename
    credit_cost = Column(Integer, default=1, nullable=False)
    book_created = Column(DateTime, default=datetime.utcnow)
    book_updated = Column(DateTime)
    section = relationship('Section', back_populates='books')
    book_requests = relationship("BookRequest", backref="book")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'authors': self.authors,
            'section_id': self.section_id,
            'file_name': self.file_name,
            'credit_cost': self.credit_cost,
            'book_created' : self.book_created,
            'book_updated' : self.book_updated
        }

class BookRequest(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    requested_date = Column(DateTime, default=datetime.utcnow)
    rejected_date = Column(DateTime)
    revoked_date = Column(DateTime)
    status = Column(Enum("requested", "granted", "rejected", "returned", "revoked"), default="requested")
    feedback = Column(Text)  # New field for feedback
    ratings = Column(Integer)
    borrowed_date = Column(DateTime)
    due_date = Column(DateTime)
    returned_date = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'status': self.status,
            'feedback': self.feedback,
            'ratings': self.ratings,
            'borrowed_date': self.borrowed_date.isoformat() if self.borrowed_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned_date': self.returned_date.isoformat() if self.returned_date else None
        }

    @hybrid_property
    def remaining_days(self):
        if self.due_date:
            remaining_days = (self.due_date - datetime.utcnow()).days
            if remaining_days < 0:
                return "Overdue"
            return remaining_days
        else:
            return None

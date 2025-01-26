
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.ext.hybrid import hybrid_property
from application.models import db

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

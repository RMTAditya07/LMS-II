from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, func
from application.api.books.models import Book
from sqlalchemy.orm import relationship
from application.extensions import db

class Section(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)

    books = relationship("Book", back_populates="section")

    def get_books_count(self):
        return db.session.query(func.count(Book.id)).filter(Book.section_id == self.id).scalar() or 0

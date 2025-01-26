from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship
from application.models import db

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

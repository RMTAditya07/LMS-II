# services/section_service.py
from application.api.books.models import Book
from application.api.requests.models import BookRequest
from .models import Section
from application.extensions import db

def get_all_sections():
    sections = Section.query.all()
    return [
        {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'book_count': Book.query.filter_by(section_id=section.id).count()
        }
        for section in sections
    ]


def create_section(name, description=None):
    if not name:
        raise ValueError("Section name is required")

    new_section = Section(name=name, description=description)
    db.session.add(new_section)
    db.session.commit()
    return new_section


def delete_section(section_id):
    section = Section.query.get(section_id)
    if not section:
        raise ValueError("Section not found")

    db.session.delete(section)
    db.session.commit()


def get_section_by_id(section_id, user_id):
    section = Section.query.get(section_id)
    if not section:
        raise ValueError("Section not found")

    books = [{'id': book.id, 'name': book.name, 'authors': book.authors} for book in section.books]
    requested_books = [
        req.book_id
        for req in BookRequest.query.filter_by(user_id=user_id)
        if req.status in ["requested", "granted"]
    ]

    return {
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'books': books,
        'requested_books': requested_books,
        'num_requested_books': len(requested_books)
    }


def update_section(section_id, data):
    section = Section.query.get(section_id)
    if not section:
        raise ValueError("Section not found")

    section.name = data.get('name', section.name)
    section.description = data.get('description', section.description)

    # Optionally handle books
    removed_books = data.get('removedBooks', [])
    for book_id in removed_books:
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)

    db.session.commit()
    return section
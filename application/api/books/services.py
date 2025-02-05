from io import BytesIO
import tempfile
from flask import session, abort, flash, send_file
from sqlalchemy.exc import IntegrityError
from application.extensions import db
from application.api.books.models import Book
from application.api.sections.models import Section
from application.api.requests.models import BookRequest
from application.api.users.models import User


def get_all_books_service(args):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    role = args.get('Role', 'student')  # Default to "student" if role is not provided

    if role == 'admin':
        # Admin view: return all books
        books = Book.query.all()
        return {'books': [book.to_dict() for book in books]}, 200

    # Student view: return books and user-specific data
    books = Book.query.all()
    num_requested_books = BookRequest.query.filter(
        (BookRequest.user_id == user_id) &
        (BookRequest.status.in_(["granted", "requested"]))
    ).count()

    requested_books = [request.book_id for request in BookRequest.query.filter_by(user_id=user_id).all() if request.status in ["requested", "granted"]]

    return {
        'books': [book.to_dict() for book in books],
        'requested_books': requested_books,
        'num_requested_books': num_requested_books,
    }, 200


def add_book_service(data, pdf_file):
    title = data.get('title')
    author = data.get('author')
    section_name = data.get('section')
    filename = data.get('filename')
    credits = data.get('credits')

    # Validate input
    if not title or not author or not section_name or not filename or not credits or not pdf_file:
        return {'error': 'All fields are required'}, 400

    # Get section
    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return {'error': 'Section not found'}, 404

    # Create and save the book
    pdf_data = pdf_file.read()
    new_book = Book(
        name=title,
        authors=author,
        section_id=section.id,
        file_name=filename,
        pdf_file=pdf_data,
        credit_cost=credits
    )
    try:
        db.session.add(new_book)
        db.session.commit()
        return {'id': new_book.id, 'name': new_book.name}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to add book'}, 500


def delete_book_service(book_id):
    book = Book.query.get(book_id)
    if not book:
        return {'error': 'Book not found'}, 404

    try:
        db.session.delete(book)
        db.session.commit()
        return {'message': 'Book deleted successfully'}, 204
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to delete book'}, 500


def download_book_service(book_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if not book:
        return abort(404, description="Book not found")
    if user and user.credit_points >= book.credit_cost:
        user.credit_points -= book.credit_cost
        db.session.commit()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(book.pdf_file)
            temp_file_path = temp_file.name

        try:
            return send_file(temp_file_path, as_attachment=True, download_name=f"{book.name}.pdf")
        except Exception as e:
            flash('An error occurred while downloading the book.', 'error')
            return {'error': 'Failed to download book'}, 500
    else:
        return {'error': 'Not enough credit points'}, 400


def view_book_service(book_id):
    book = Book.query.get(book_id)
    if not book:
        return abort(404, description="Book not found")

    # Serve the PDF file directly
    pdf_data = BytesIO(book.pdf_file)
    return send_file(
        pdf_data,
        download_name=book.file_name,
        mimetype='application/pdf'
    )


def get_book_service(book_id):
    book = Book.query.get(book_id)
    if not book:
        return {'error': 'Book not found'}, 404

    sections = Section.query.all()
    return {
        'name': book.name,
        'section_id': book.section_id,
        'authors': book.authors,
        'credit_cost': book.credit_cost,
        'file_name': book.file_name,
        'sections': [{'id': sec.id, 'name': sec.name} for sec in sections]
    }, 200


def update_book_service(book_id, data, file):
    book = Book.query.get(book_id)
    if not book:
        return {'error': 'Book not found'}, 404

    # Update fields
    book.name = data.get('name', book.name)
    book.section_id = data.get('section_id', book.section_id)
    book.authors = data.get('authors', book.authors)
    book.credit_cost = data.get('credit_cost', book.credit_cost)
    book.file_name = data.get('file_name', book.file_name)

    if file:
        # Update the PDF file
        book.pdf_file = file.read()

    try:
        db.session.commit()
        return {'success': True}, 200
    except IntegrityError:
        db.session.rollback()
        return {'success': False, 'message': 'Database error occurred.'}, 500


def get_reviews_service(book_id):
    reviews = BookRequest.query.filter_by(book_id=book_id).all()

    if not reviews:
        return {'reviews': [], 'consolidated_rating': None}, 200

    review_list = []
    total_rating = 0
    valid_ratings_count = 0

    for review in reviews:
        if review.ratings is not None:  # Ignore None ratings
            review_list.append({
                'id': review.id,
                'username': review.user.username,  # Assuming `user` relationship exists
                'rating': review.ratings,
                'feedback': review.feedback
            })
            total_rating += review.ratings
            valid_ratings_count += 1

    consolidated_rating = round(total_rating / valid_ratings_count, 1) if valid_ratings_count > 0 else None

    return {
        'reviews': review_list,
        'consolidated_rating': consolidated_rating
    }, 200
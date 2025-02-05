from datetime import datetime, timedelta, timezone
from flask import session
from application.api.books.models import Book
from application.api.requests.models import BookRequest
from application.api.sections.models import Section
from application.api.users.models import User
from application.extensions import db

def format_date(date):
    if date:
        return date.strftime('%d/%m/%Y')
    return None


def get_requests_by_status_service(status):
    valid_statuses = ['requested', 'granted', 'returned', 'revoked', 'rejected']
    if status not in valid_statuses:
        return {'error': 'Invalid status'}, 400

    try:
        requests = db.session.query(BookRequest, Book, User, Section).join(
            Book, BookRequest.book_id == Book.id
        ).join(
            User, BookRequest.user_id == User.id
        ).join(
            Section, Book.section_id == Section.id
        ).filter(BookRequest.status == status).all()

        requests_list = [{
            'id': req.BookRequest.id,
            'book_name': req.Book.name,
            'name': req.User.name,
            'section_name': req.Section.name,
            'requested_date': format_date(req.BookRequest.requested_date),
            'borrowed_date': format_date(req.BookRequest.borrowed_date),
            'due_date': format_date(req.BookRequest.due_date),
            'returned_date': format_date(req.BookRequest.returned_date),
            'revoked_date': format_date(req.BookRequest.revoked_date),
            'rejected_date': format_date(req.BookRequest.rejected_date),
            'feedback': req.BookRequest.feedback or 'N/A',
            'ratings': req.BookRequest.ratings or 'N/A',
            'status': req.BookRequest.status,
            'remaining_days': (req.BookRequest.due_date - datetime.now()).days if req.BookRequest.due_date else None,
        } for req in requests]

        return {'requests': requests_list, 'count': len(requests_list)}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def approve_request_service(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'granted'
        request.borrowed_date = datetime.now()
        request.due_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        db.session.commit()
        return {'message': 'Request approved successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def reject_request_service(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'rejected'
        request.rejected_date = datetime.now()
        db.session.commit()
        return {'message': 'Request rejected successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def revoke_request_service(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'revoked'
        request.revoked_date = datetime.now()
        db.session.commit()
        return {'message': 'Request revoked successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def create_book_request_service(data):
    book_id = data.get('book_id')
    user_id = session.get('user_id')

    if not book_id:
        return {'message': 'Book ID is required'}, 400

    book = Book.query.get(book_id)
    if not book:
        return {'message': 'Book not found'}, 404

    existing_request = BookRequest.query.filter_by(book_id=book_id, user_id=user_id, status='requested').first()
    if existing_request:
        return {'message': 'Book already requested'}, 400

    new_request = BookRequest(book_id=book_id, user_id=user_id, status='requested')
    db.session.add(new_request)
    db.session.commit()
    return {'message': 'Book request created successfully'}, 201


def get_user_book_requests_service():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'User not authenticated'}, 401

        user_requests = db.session.query(BookRequest, Book, Section).join(
            Book, BookRequest.book_id == Book.id
        ).join(
            Section, Book.section_id == Section.id
        ).filter(
            BookRequest.user_id == user_id
        ).all()

        requests_data = []
        for request, book, section in user_requests:
            request_data = {
                'request_id': request.id,
                'book_id': book.id,
                'book_name': book.name,
                'status': request.status,
                'requested_date': format_date(request.requested_date),
                'section_name': section.name,
                'borrowed_date': format_date(request.borrowed_date),
                'due_date': format_date(request.due_date)
            }

            if request.status == 'granted':
                request_data['remaining_days'] = (request.due_date - datetime.now()).days if request.due_date else None

            elif request.status == 'rejected':
                request_data.update({
                    'rejected_date': format_date(request.rejected_date) if request.rejected_date else None,
                })
            elif request.status == 'returned':
                request_data.update({
                    'returned_date': format_date(request.returned_date) if request.returned_date else None,
                    'feedback': request.feedback,
                    'ratings': request.ratings
                })
            elif request.status == 'revoked':
                request_data.update({
                    'revoked_date': format_date(request.revoked_date) if request.revoked_date else None,
                })
            
            requests_data.append(request_data)

        return {'requests': requests_data}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def return_book_service(book_request_id, data):
    try:
        borrowed_book = BookRequest.query.get_or_404(book_request_id)
        feedback = data.get('feedback')
        ratings = data.get('ratings')
        returned_date = datetime.now()

        remaining_days = (borrowed_book.due_date - returned_date).days
        penalty = abs(remaining_days) * 2 if remaining_days < 0 else 0

        borrowed_book.status = "returned"
        borrowed_book.feedback = feedback
        borrowed_book.ratings = ratings
        borrowed_book.returned_date = returned_date

        user = User.query.get(borrowed_book.user_id)
        if user:
            user.credit_points -= penalty

        db.session.commit()
        return {'message': 'Book returned successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500
    
    
    
def get_accepted_books(user_id):
    try:
        
        # Query for BookRequests with status 'granted' and join with Book and Section, filtered by user_id
        accepted_requests = db.session.query(BookRequest, Book, Section).\
            join(Book, BookRequest.book_id == Book.id).\
            join(Section, Book.section_id == Section.id).\
            filter(BookRequest.status == 'granted', BookRequest.user_id == user_id).\
            all()

        # Format the results
        result = []
        for request, book, section in accepted_requests:
            result.append({
                'request_id': request.id,
                'book_id': book.id,
                'book_name': book.name,
                'authors': book.authors,
                'section_name': section.name,
                'borrowed_date': format_date(request.borrowed_date) if request.borrowed_date else None,
                'due_date': format_date(request.due_date) if request.due_date else None,
                'remaining_days': (request.due_date - datetime.now()).days if request.due_date else None
            })

        return {'accepted_books': result}
    except Exception as e:
        return {'error': str(e)}, 500

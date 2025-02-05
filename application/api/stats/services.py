from datetime import datetime, timedelta
from sqlalchemy.sql import text
from application.extensions import db
from application.api.books.models import Book
from application.api.requests.models import BookRequest
from application.api.sections.models import Section
from application.api.users.models import User


def get_statistics_service(stat_type):
    if stat_type == 'books_by_section':
        sections = db.session.query(Section.name, db.func.count(Book.id)).join(Book).group_by(Section.id).all()
        return dict(sections)
    elif stat_type == "requests_by_section":
        requests = db.session.query(Section.name, db.func.count(BookRequest.id)).join(Book, Book.section_id == Section.id).join(BookRequest).group_by(Section.id).all()
        return dict(requests)
    elif stat_type == "total_requests":
        total = db.session.query(db.func.count(BookRequest.id)).scalar()
        return {'total_requests': total}
    elif stat_type == "total_users":
        total_users = db.session.query(db.func.count(User.id)).scalar()
        total_books = db.session.query(db.func.count(Book.id)).scalar()
        total_sections = db.session.query(db.func.count(Section.id)).scalar()
        return {
            'total_users': total_users,
            'total_books': total_books,
            'total_sections': total_sections
        }
    elif stat_type == "most_requested_books":
        books = db.session.query(Book.name, db.func.count(BookRequest.id)).join(BookRequest).group_by(Book.id).order_by(db.func.count(BookRequest.id).desc()).limit(10).all()
        return dict(books)
    elif stat_type == "average_rating_by_book":
        avg_ratings = db.session.query(Book.name, db.func.avg(BookRequest.ratings)).join(BookRequest).group_by(Book.id).all()
        return dict(avg_ratings)
    elif stat_type == "users_enrolled_each_month":
        start_date = datetime(datetime.now().year, 1, 1)
        end_date = datetime(datetime.now().year + 1, 1, 1)
        results = db.session.query(
            db.func.date_trunc('month', User.date_joined).label('month'),
            db.func.count(User.id).label('count')
        ).filter(User.date_joined >= start_date, User.date_joined < end_date).group_by(
            db.func.date_trunc('month', User.date_joined)
        ).order_by('month').all()
        return {result.month.strftime('%B %Y'): result.count for result in results}
    elif stat_type == "total_requests_each_month":
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        query = text('''
            SELECT strftime('%Y-%m', requested_date) AS month, COUNT(id) AS count
            FROM book_request
            WHERE requested_date >= :start_date AND requested_date < :end_date
            GROUP BY strftime('%Y-%m', requested_date)
            ORDER BY month
        ''')
        results = db.session.execute(query, {'start_date': start_date, 'end_date': end_date}).fetchall()
        return {row[0]: row[1] for row in results}
    else:
        raise ValueError("Invalid statistics type")

def get_student_statistics_service(user_id):
    total_books_borrowed = BookRequest.query.filter_by(user_id=user_id).count()
    books_returned_on_time = BookRequest.query.filter(
        BookRequest.user_id == user_id,
        BookRequest.returned_date <= BookRequest.due_date
    ).count()
    total_ratings = db.session.query(db.func.sum(BookRequest.ratings)).filter_by(user_id=user_id).scalar() or 0
    total_feedbacks = BookRequest.query.filter_by(user_id=user_id).count()
    average_rating = total_feedbacks > 0 and total_ratings / total_feedbacks or 0
    pending_requests = BookRequest.query.filter_by(user_id=user_id, status='requested').count()
    overdue_books = BookRequest.query.filter(
        BookRequest.user_id == user_id,
        BookRequest.due_date < datetime.now(),
        BookRequest.returned_date.is_(None)
    ).count()
    favorite_section = db.session.query(Section).join(Book).join(BookRequest).filter(
        BookRequest.user_id == user_id
    ).group_by(Section.id).order_by(db.func.count(BookRequest.id).desc()).first()
    favorite_section_name = favorite_section.name if favorite_section else 'None'
    return {
        'totalBooksBorrowed': total_books_borrowed,
        'booksReturnedOnTime': books_returned_on_time,
        'averageRating': average_rating,
        'pendingRequests': pending_requests,
        'overdueBooks': overdue_books,
        'favoriteSection': favorite_section_name
    }

def get_admin_statistics_service():
    total_users = db.session.query(db.func.count(User.id)).scalar()
    granted_requests = db.session.query(db.func.count(BookRequest.id)).filter_by(status='granted').scalar()
    ebooks_issued = db.session.query(db.func.count(Book.id)).filter(Book.pdf_file.isnot(None)).scalar()
    revoked_requests = db.session.query(db.func.count(BookRequest.id)).filter_by(status='revoked').scalar()
    rejected_requests = db.session.query(db.func.count(BookRequest.id)).filter_by(status='rejected').scalar()
    overdue_requests = db.session.query(db.func.count(BookRequest.id)).filter(
        BookRequest.due_date < db.func.current_date(), BookRequest.status != 'returned'
    ).scalar()
    pending_requests = db.session.query(db.func.count(BookRequest.id)).filter_by(status='requested').scalar()
    return {
        'activeUsers': total_users,
        'grantedRequests': granted_requests,
        'ebooksIssued': ebooks_issued,
        'revokedRequests': revoked_requests,
        'rejectedRequests': rejected_requests,
        'overdueRequests': overdue_requests,
        'pendingRequests': pending_requests
    }

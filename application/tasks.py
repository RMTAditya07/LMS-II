from celery import shared_task
from jinja2 import Template
from sqlalchemy import func
from .models import BookRequest, Book, Role, User, Section,db
# from flask_mail import Mail, Message
import csv
import io
import os
import flask_excel as excel
from datetime import datetime, timedelta
from .mail_service import generate_html_report, send_message, send_reminders

@shared_task(ignore_result=False)
def export_section_to_csv():
    sec_res = Section.query.with_entities(Section.id,Section.name, Section.description).all()
    csv_output = excel.make_response_from_query_sets(sec_res, ["id","name","description"],"csv")
    filename="sections.csv"
    
    with open(filename, 'wb')as f:
        f.write(csv_output.data)
    return filename

@shared_task(ignore_result=False)
def export_books_to_csv():
    books_res = Book.query.with_entities(Book.id,Book.name, Book.authors,Book.section_id,Book.credit_cost).all()
    
    csv_output = excel.make_response_from_query_sets(books_res, ["id","name","authors","section_id","credit_cost"],"csv")
    filename="books.csv"
    
    with open(filename, 'wb')as f:
        f.write(csv_output.data)
    return filename

@shared_task(ignore_result=False)
def export_book_request_to_csv():
    try:
        # Query BookRequest with Book and Section details
        book_requests_res = db.session.query(
            BookRequest.id.label('request_id'),
            Book.name.label('book_name'),
            Section.name.label('section_name'),
            BookRequest.status,
            BookRequest.requested_date,
            BookRequest.borrowed_date,
            BookRequest.due_date,
            BookRequest.returned_date,
        ).join(Book, BookRequest.book_id == Book.id)\
         .join(Section, Book.section_id == Section.id)\
         .all()

        # Prepare CSV data
        csv_data = [['request_id', 'book_name', 'section_name', 'status', 'requested_date','borrowed_date','due_date','returned_date']]
        for req in book_requests_res:
            csv_data.append([
                req.request_id,
                req.book_name,
                req.section_name,
                req.status,
                req.borrowed_date.strftime('%Y-%m-%d') if req.borrowed_date else None,
                req.requested_date.strftime('%Y-%m-%d') if req.requested_date else None,
                req.due_date.strftime('%Y-%m-%d') if req.due_date else None,
                req.returned_date.strftime('%Y-%m-%d') if req.returned_date else None
            ])

        # Save to CSV file
        filename = "book_requests.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

        return filename

    except Exception as e:
        return str(e)
    
@shared_task(ignore_result=False)
def generate_monthly_report(to, subject):
    today = datetime.today()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    try:
        book_requests = db.session.query(
            BookRequest.id,
            Book.name.label('book_name'),
            Section.name.label('section_name'),
            User.name.label('user_name'),
            BookRequest.requested_date,
            BookRequest.status,
            BookRequest.ratings,
            BookRequest.borrowed_date,
            BookRequest.due_date,
            BookRequest.returned_date
        ).join(Book, BookRequest.book_id == Book.id)\
        .join(User, BookRequest.user_id == User.id)\
        .join(Section, Book.section_id == Section.id)\
        .filter(BookRequest.requested_date.between(first_day, last_day)).all()
    except Exception as e:
        return f"Error fetching book requests: {str(e)}"

    results = []
    for request in book_requests:
        if request.returned_date:
            remaining_days = 0
        else:
            if request.due_date:
                remaining_days = (request.due_date - datetime.now()).days
                remaining_days = max(remaining_days, 0)
            else:
                remaining_days = "No Due Date"

        results.append({
            'id': request.id,
            'book_name': request.book_name,
            'section_name': request.section_name,
            'user_name': request.user_name,
            'requested_date': format_date(request.requested_date),
            'status': request.status,
            'ratings': request.ratings,
            'borrowed_date': format_date(request.borrowed_date),
            'due_date': format_date(request.due_date),
            'returned_date': format_date(request.returned_date),
            'remaining_days': remaining_days
        })

    section_data = []
    for section in Section.query.all():
        book_count = Book.query.filter_by(section_id=section.id).count()
        section_data.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'book_count': book_count
        })

    book_request_counts = db.session.query(
        Book.id,
        Book.name.label('book_name'),
        Book.authors,
        func.count(BookRequest.id).label('request_count')
    ).outerjoin(BookRequest, Book.id == BookRequest.book_id)\
    .group_by(Book.id)\
    .all()

    try:
        users = User.query.filter(User.roles.any(Role.name == "admin")).all()
    except Exception as e:
        return f"Error fetching users: {str(e)}"

    html_report = generate_html_report(section_data, results, book_request_counts)
    
    for user in users:
        try:
            send_message(user.email, subject, html_report)
        except Exception as e:
            return f"Error sending email to {user.email}: {str(e)}"

    return "Report generated and emails sent successfully"
        
@shared_task(ignore_result=False)        
def send_daily_reminders():
    send_reminders()
        
def format_date(date):
    """Format date as a string."""
    return date.strftime('%Y-%m-%d') if date else None

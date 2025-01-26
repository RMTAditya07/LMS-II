from datetime import datetime, timedelta
from flask import jsonify
from application.api.books.models import Book
from application.api.requests.models import BookRequest
from application.api.sections.models import Section
from application.tasks import export_book_request_to_csv, export_books_to_csv, export_section_to_csv
from celery.result import AsyncResult


def export_csv_service(export_type):
    """
    Handles CSV export logic for sections, books, or book requests.
    """
    if export_type == 'sections':
        task = export_section_to_csv.delay()
    elif export_type == 'books':
        task = export_books_to_csv.delay()
    elif export_type == 'book_requests':
        task = export_book_request_to_csv.delay()
    else:
        return {"error": "Invalid export type"}, 400  # Bad Request

    return {"task_id": task.id}, 200


def get_csv_service(task_id):
    """
    Retrieves the status or result of a given CSV export task.
    """
    res = AsyncResult(task_id)
    if res.ready():
        return {"filename": res.result}, 200
    else:
        return {"message": "Task Pending"}, 404


def generate_monthly_report():
    """
    Prepares a monthly report of sections and book requests.
    """
    today = datetime.today()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    sections = Section.query.all()
    book_requests = BookRequest.query.filter(BookRequest.requested_date.between(first_day, last_day)).all()

    section_data = []
    for section in sections:
        book_count = Book.query.filter_by(section_id=section.id).count()
        section_data.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'book_count': book_count
        })

    return {
        "sections": section_data,
        "book_requests": book_requests
    }

from datetime import datetime, timedelta, timezone
from io import BytesIO
import io
import os
from sqlite3 import IntegrityError
import tempfile
from flask import abort, current_app as app, flash, jsonify, render_template, request, send_file, session
from flask_security import auth_required, roles_required, roles_accepted, current_user
from sqlalchemy import func, text
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_restful import marshal, fields
from celery.result import AsyncResult
import flask_excel as excel
from .tasks import export_book_request_to_csv, export_books_to_csv, export_section_to_csv
# from .tasks import create_resource_csv
from .models import User, db, Book, BookRequest, Section
from .sec import datastore
from .instances import cache


# Function to format dates
def format_date(date):
            if date:
                return date.strftime('%d/%m/%Y')
            return None


@app.get('/')
def home():
    return render_template("index.html")

@app.get('/admin')
@auth_required("token")
@roles_required("admin")
def admin():
    return "Welcome admin"


@app.get('/activate/inst/<int:inst_id>')
@auth_required("token")
@roles_required("admin")
def activate_instructor(inst_id):
    instructor = User.query.get(inst_id)
    if not instructor or "inst" not in [role.name for role in instructor.roles]:
        return jsonify({"message": "Instructor not found"}), 404
    instructor.active = True
    db.session.commit()
    return jsonify({"message": "Instructor activated successfully"}), 200


@app.post('/user-login')
def user_login():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"message": "Missing email"}), 400
    
    user = datastore.find_user(email=email)
    session['user_id'] = user.id 
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if check_password_hash(user.password, data.get('password')):
        return jsonify({"token" : user.get_auth_token(), "email" : user.email, "role":user.roles[0].name, "user_id":user.id})
    
    else:
        return jsonify({"message" : "Wrong Password"}),400
    
@app.get('/api/credit-points')
@auth_required()  # Ensure the user is authenticated
def get_user_credit_points():
    user_id = current_user.id
    user = db.session.query(User).filter_by(id=user_id).first()  # Adjust based on your User model
    
    if user:
        return jsonify({'creditPoints': user.credit_points})
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/api/update_last_visit', methods=['POST'])
def update_last_visit():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.last_visit_date = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Last visit date updated successfully'}), 200
    


user_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "active":fields.Boolean,
    "last_visit_date" : fields.DateTime,
    "date_joined":fields.DateTime,
    "credit_points":fields.Integer,
    "username" : fields.String,
    "name":fields.String
}

@app.get('/users')
@auth_required("token")
@roles_required("admin")
def all_users():
    users = User.query.all()
    if len(users) == 0:
        return jsonify({"message": "No users found"}), 404
    return marshal(users, user_fields)

    
@app.get('/api/sections')
@auth_required("token")
@roles_accepted('admin', 'student')
# @cache.cached(timeout=30)
def get_sections():
    sections = Section.query.all()
    section_data = []
    for section in sections:
        book_count = Book.query.filter_by(section_id=section.id).count()
        section_data.append({'id': section.id, 'name': section.name, 'description':section.description,'book_count': book_count})
    return jsonify(section_data)

@app.post('/api/sections')
@auth_required("token")
@roles_required("admin")
def add_section():
    section_name = request.form.get('section_name')
    section_desc = request.form.get('section_desc')
    if not section_name:
        return jsonify({'error': 'Section name is required'}), 400
    
    new_section = Section(name=section_name, description= section_desc)
    db.session.add(new_section)
    db.session.commit()
    return jsonify({'id': new_section.id, 'name': new_section.name, 'description':new_section.description}), 201


@app.delete('/api/sections/<int:id>')
# @cache.cached(timeout=30)
def delete_section(id):
    section = Section.query.get_or_404(id)
    db.session.delete(section)
    db.session.commit()
    return '', 204

# Routes for Books
@app.get('/api/books')  
@auth_required("token")
@roles_accepted('admin', 'student')
# @cache.cached(timeout=30)
def get_books():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    role = request.headers.get('Role')

    if role == 'admin':
        # Admin view: return all books
        books = Book.query.all()
        return jsonify({'books': [book.to_dict() for book in books]})
    
    # Student view: return books and user-specific data
    books = Book.query.all()
    num_requested_books = BookRequest.query.filter(
        (BookRequest.user_id == user_id) & 
        (BookRequest.status.in_(["granted", "requested"]))
    ).count()

    requested_books = [request.book_id for request in BookRequest.query.filter_by(user_id=user_id).all() if request.status in ["requested", "granted"]]

    return jsonify({
        'books': [book.to_dict() for book in books],
        'requested_books': requested_books,
        'num_requested_books': num_requested_books,
    })
    
    
@app.post('/api/books')
@auth_required("token")
@roles_required("admin")
def add_book():
    # Access form data
    title = request.form.get('title')
    author = request.form.get('author')
    section_name = request.form.get('section')
    filename = request.form.get('filename')
    credits = request.form.get('credits')
    
    # Access the uploaded file
    pdf_file = request.files.get('pdf_file')
    
    # Validate the received data
    if not title or not author or not section_name or not filename or not credits or not pdf_file:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Create and save the new book
    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return jsonify({'error': 'Section not found'}), 404

    pdf_data = pdf_file.read()
    
    new_book = Book(
        name=title,
        authors=author,
        section_id=section.id,
        file_name=filename,
        pdf_file = pdf_data,
        credit_cost=credits
    )
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({'id': new_book.id, 'name': new_book.name}), 201

@app.delete('/api/books/<int:id>')
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return '', 204

@app.get('/api/download_pdf/<int:book_id>')
def download_pdf(book_id):
    # Query the database for the book with the given ID
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    if not book:
        abort(404, description="Book not found")
    if book and user:
        if user.credit_points >= book.credit_cost:
            user.credit_points -= book.credit_cost
            db.session.commit()
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(book.pdf_file)
                        temp_file_path = temp_file.name
            try:
                return send_file(temp_file_path, as_attachment=True, download_name=f"{book.name}.pdf")
            except Exception as e:
                flash('An error occurred while downloading the book.', 'error')
                return 
        else:
            return({'You do not have enough credit points to download this book.', }),400
        
@app.get('/api/view_pdf/<int:book_id>')
def view_pdf(book_id):
    # Query the database for the book with the given ID
    book = Book.query.get(book_id)
    if not book:
        abort(404, description="Book not found")

    # Create a BytesIO object and write the PDF data to it
    pdf_data = BytesIO(book.pdf_file)
    
    # Set the filename for the PDF
    filename = book.file_name

    return send_file(
        pdf_data,
        download_name=filename,
        mimetype='application/pdf'
    )

@app.get('/api/section/<int:section_id>')
def get_section(section_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    section = Section.query.get(section_id)
    if section:
        books = [{'id': book.id, 'name': book.name, 'authors': book.authors} for book in section.books]
        num_requested_books = BookRequest.query.join(BookRequest.book).filter(
            (BookRequest.user_id == user_id) &
            (BookRequest.status.in_(["granted", "requested"]))
        ).count()
        
        requested_books = [request.book_id for request in BookRequest.query.filter_by(user_id=user_id).all() if request.status in ["requested", "granted"]]

        
        return jsonify({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'books': books,
            'requested_books': requested_books,
            'num_requested_books': num_requested_books,
        })
    else:
        return jsonify({'error': 'Section not found'}), 404
    
@app.put('/api/sections/<int:section_id>')
def update_section(section_id):
    data = request.get_json()
    section = Section.query.get(section_id)
    if section:
        section.name = data.get('name', section.name)
        section.description = data.get('description', section.description)

        # Optionally handle books
        removed_books = data.get('removedBooks', [])
        for book_id in removed_books:
            book = Book.query.get(book_id)
            if book:
                db.session.delete(book)
        
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Section not found'}), 404
    

@app.get('/api/books/<int:book_id>')
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    sections = Section.query.all()
    return jsonify({
        'name': book.name,
        'section_id': book.section_id,
        'authors': book.authors,
        'credit_cost': book.credit_cost,
        'file_name': book.file_name,
        'sections': [{'id': sec.id, 'name': sec.name} for sec in sections]
    })
    
@app.put('/api/books/<int:book_id>')
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.form
    file = request.files.get('pdf_file')

    book.name = data.get('name')
    book.section_id = data.get('section_id')
    book.authors = data.get('authors')
    book.credit_cost = data.get('credit_cost')
    book.file_name = data.get('file_name')

    if file:
        # Read the file content and store as binary in the database
        book.pdf_file = file.read()

    try:
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred.'})

@app.get('/api/books/<int:book_id>/file')
def get_book_file(book_id):
    book = Book.query.get_or_404(book_id)
    if book.pdf_file:
        return send_file(
            io.BytesIO(book.pdf_file),
            as_attachment=True,
            attachment_filename=book.file_name,
            mimetype='application/pdf'
        )
    return jsonify({'message': 'File not found.'}), 404

@app.route('/api/requests/<status>', methods=['GET'])
@auth_required("token")
@roles_required("admin")
def get_requests_by_status(status):
    valid_statuses = ['requested', 'granted', 'returned', 'revoked', 'rejected']
    if status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        # Query to fetch requests based on status
        requests = db.session.query(BookRequest, Book, User, Section).\
            join(Book, BookRequest.book_id == Book.id).\
            join(User, BookRequest.user_id == User.id).\
            join(Section, Book.section_id == Section.id).\
            filter(BookRequest.status == status).all()

        # Convert query results to list of dictionaries
        requests_list = [{
            'id': req.BookRequest.id,
            'book_name': req.Book.name,
            'name': req.User.name,
            'section_name': req.Section.name,
            'requested_date': format_date(req.BookRequest.requested_date),
            'borrowed_date': format_date(req.BookRequest.borrowed_date),
            'due_date': format_date(req.BookRequest.due_date) if req.BookRequest.due_date else None,
            'returned_date': format_date(req.BookRequest.returned_date) if req.BookRequest.returned_date else None,
            'revoked_date': format_date(req.BookRequest.revoked_date) if req.BookRequest.revoked_date else None,
            'rejected_date': format_date(req.BookRequest.rejected_date) if req.BookRequest.rejected_date else None,
            'feedback': req.BookRequest.feedback if req.BookRequest.feedback else 'N/A',
            'ratings': req.BookRequest.ratings if req.BookRequest.ratings else 'N/A',
            'status': req.BookRequest.status,
            'remaining_days': (req.BookRequest.due_date - datetime.now()).days if req.BookRequest.due_date else None
        } for req in requests]

        return jsonify({'requests': requests_list, 'count': len(requests_list)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/api/requests/<int:request_id>/approve')
def approve_request(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'granted'
        request.borrowed_date = datetime.now()
        request.due_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        db.session.commit()
        return jsonify({'message': 'Request approved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/api/requests/<int:request_id>/reject')
def reject_request(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'rejected'
        request.rejected_date = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Request rejected successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post('/api/requests/<int:request_id>/revoke')
def revoke_request(request_id):
    try:
        request = BookRequest.query.get_or_404(request_id)
        request.status = 'revoked'
        request.revoked_date = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Request revoked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.post('/api/requests')
@auth_required("token")
@roles_required("student")
def create_book_request():
    data = request.get_json()
    book_id = data.get('book_id')
    user_id = session.get('user_id')
    print("User id : ",user_id)

    if not book_id:
        return jsonify({'message': 'Book ID is required'}), 400

    # Check if the book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    # Check if the user has already requested this book
    existing_request = BookRequest.query.filter_by(book_id=book_id, user_id=user_id, status='requested').first()
    if existing_request:
        return jsonify({'message': 'Book already requested'}), 400

    # Create a new book request
    new_request = BookRequest(book_id=book_id, user_id=user_id, status='requested')
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Book request created successfully'}), 201

@app.get('/api/book-requests')
def get_user_book_requests():
    try:
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # Fetch book requests for the specific user and join with Book and Section
        user_requests = db.session.query(BookRequest, Book, Section).join(
            Book, BookRequest.book_id == Book.id
        ).join(
            Section, Book.section_id == Section.id
        ).filter(
            BookRequest.user_id == user_id
        ).all()

        # Convert requests to dictionary format based on status
        requests_data = []
        for request, book, section in user_requests:
            request_data = {
                'request_id': request.id,
                'book_id': book.id,
                'book_name': book.name,
                'status':request.status,
                'requested_date':format_date(request.requested_date),
                'section_name': section.name,
                'borrowed_date': format_date(request.borrowed_date) if request.borrowed_date else None,
                'due_date': format_date(request.due_date) if request.due_date else None
            }

            if request.status == 'granted':
                request_data.update({
                    'authors': book.authors,
                    'remaining_days': (request.due_date - datetime.now()).days if request.due_date else None
                })
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
            # Add additional status checks if needed

            requests_data.append(request_data)

        return jsonify({'requests': requests_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get('/api/accepted-books')
@auth_required()  # Ensure the user is authenticated
@roles_accepted('student')
def get_accepted_books():
    try:
        # Get the current user's ID
        user_id = session.get('user_id')

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

        return jsonify({'accepted_books': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None

@app.put('/api/book-requests/<int:book_request_id>/return')
def return_book(book_request_id):
    try:
        borrowed_book = BookRequest.query.filter_by(id=book_request_id).first()
        
        if borrowed_book:
            data = request.json
            feedback = data.get('feedback')
            ratings = data.get('ratings')
            returned_date = datetime.now()
            
            remaining_days = (borrowed_book.due_date - returned_date).days
            penalty = 0
                
            if remaining_days < 0:
                penalty = abs(remaining_days) * 2
                
            # Update the status and feedback
            borrowed_book.status = "returned"
            borrowed_book.feedback = feedback
            borrowed_book.ratings = ratings
            borrowed_book.returned_date = returned_date
            
            user = User.query.filter_by(id=borrowed_book.user_id).first()
            if user:
                user.credit_points -= penalty
                db.session.commit()
            db.session.commit()

            return jsonify({'message': 'Book returned successfully'})

        return jsonify({'error': 'Borrowed book not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get('/api/book/<int:book_id>/reviews')
def get_reviews(book_id):
    reviews = BookRequest.query.filter_by(book_id=book_id).all()
    
    if not reviews:
        return jsonify({'reviews': [], 'consolidated_rating': None})
    
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
    
    consolidated_rating = None
    if valid_ratings_count > 0:
        consolidated_rating = round(total_rating / valid_ratings_count, 1)
    
    return jsonify({
        'reviews': review_list,
        'consolidated_rating': consolidated_rating
    })
    
@app.get('/api/stats')
def get_statistics():
    stat_type = request.args.get('type')
    if(stat_type == 'books_by_section'):
        sections = db.session.query(Section.name, db.func.count(Book.id)).join(Book).group_by(Section.id).all()
        return jsonify(dict(sections))
    elif stat_type == "requests_by_section":
        requests = db.session.query(Section.name, db.func.count(BookRequest.id)).join(Book, Book.section_id == Section.id).join(BookRequest).group_by(Section.id).all()
        return jsonify(dict(requests))
    elif stat_type == "total_requests":
        total = db.session.query(db.func.count(BookRequest.id)).scalar()
        return jsonify({'total_requests': total})
    elif stat_type == "total_users":
        total_users = db.session.query(db.func.count(User.id)).scalar()
        total_books = db.session.query(db.func.count(Book.id)).scalar()
        total_sections = db.session.query(db.func.count(Section.id)).scalar()
        return jsonify({
            'total_users': total_users,
            'total_books': total_books,
            'total_sections': total_sections
        })
    elif stat_type == "most_requested_books":
        books = db.session.query(Book.name, db.func.count(BookRequest.id)).join(BookRequest).group_by(Book.id).order_by(db.func.count(BookRequest.id).desc()).limit(10).all()
        return jsonify(dict(books))
        
    elif stat_type == "average_rating_by_book":
        avg_ratings = db.session.query(Book.name, db.func.avg(BookRequest.ratings)).join(BookRequest).group_by(Book.id).all()
        return jsonify(dict(avg_ratings))
        
    elif stat_type == "users_enrolled_each_month":
        # Calculate the start of the current year
        start_date = datetime(datetime.now().year, 1, 1)
        # Calculate the end of the current year
        end_date = datetime(datetime.now().year + 1, 1, 1)
        
        # Query to count users enrolled each month
        results = db.session.query(
            func.date_trunc('month', User.date_joined).label('month'),
            func.count(User.id).label('count')
        ).filter(User.date_joined >= start_date, User.date_joined < end_date) \
        .group_by(func.date_trunc('month', User.date_joined)) \
        .order_by('month') \
        .all()

        data = {result.month.strftime('%B %Y'): result.count for result in results}
        return jsonify(data)
        
    elif stat_type == "total_requests_each_month":
        # Calculate the start and end dates for the past year
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
        data = {row[0]: row[1] for row in results}  # Access by index instead of key
        return jsonify(data)
        

@app.route('/api/stats/student')
def get_student_statistics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        total_books_borrowed = BookRequest.query.filter_by(user_id=user_id).count()

        books_returned_on_time = BookRequest.query.filter(
            BookRequest.user_id == user_id,
            BookRequest.returned_date <= BookRequest.due_date
        ).count()

        total_ratings = db.session.query(db.func.sum(BookRequest.ratings)).filter_by(user_id=user_id).scalar()
        # Ensure total_ratings is not None
        total_ratings = total_ratings if total_ratings is not None else 0
        total_feedbacks = BookRequest.query.filter_by(user_id=user_id).count()
        average_rating = total_feedbacks > 0 and total_ratings / total_feedbacks or 0

        pending_requests = BookRequest.query.filter_by(user_id=user_id, status='requested').count()
        overdue_books = BookRequest.query.filter(
            BookRequest.user_id == user_id,
            BookRequest.due_date < datetime.now(),
            BookRequest.returned_date.is_(None)
        ).count()

        # Get the favorite section
        favorite_section = db.session.query(Section).join(Book).join(BookRequest).filter(
            BookRequest.user_id == user_id
        ).group_by(Section.id).order_by(func.count(BookRequest.id).desc()).first()

        favorite_section_name = favorite_section.name if favorite_section else 'None'

        statistics = {
            'totalBooksBorrowed': total_books_borrowed,
            'booksReturnedOnTime': books_returned_on_time,
            'averageRating': average_rating,
            'pendingRequests': pending_requests,
            'overdueBooks': overdue_books,
            'favoriteSection': favorite_section_name
        }

        return jsonify(statistics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.get('/api/stats/admin')
def get_admin_statistics():
    try:
        # Example queries to fetch statistics
        total_users = db.session.query(func.count().label('count')).select_from(User).scalar()
        granted_requests = db.session.query(func.count().label('count')).select_from(BookRequest).filter_by(status='granted').scalar()
        ebooks_issued = db.session.query(func.count().label('count')).select_from(Book).filter(Book.pdf_file.isnot(None)).scalar()
        revoked_requests = db.session.query(func.count().label('count')).select_from(BookRequest).filter_by(status='revoked').scalar()
        rejected_requests = db.session.query(func.count().label('count')).select_from(BookRequest).filter_by(status='rejected').scalar()
        overdue_requests = db.session.query(func.count().label('count')).select_from(BookRequest).filter(BookRequest.due_date < func.current_date(), BookRequest.status != 'returned').scalar()
        pending_requests = db.session.query(func.count().label('count')).select_from(BookRequest).filter_by(status='requested').scalar()

        # Example data structure for response
        stats = {
            'activeUsers': total_users,
            'grantedRequests': granted_requests,
            'ebooksIssued': ebooks_issued,
            'revokedRequests': revoked_requests,
            'rejectedRequests': rejected_requests,
            'overdueRequests': overdue_requests,
            'pendingRequests': pending_requests
        }
        
        return jsonify(stats)
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500


@app.get('/api/export/csv')
def export_csv():
    """
    Unified route to export CSV for sections, books, or book requests.
    Use query parameter `type` to specify export type.
    """
    export_type = request.args.get('type')

    if export_type == 'sections':
        task = export_section_to_csv.delay()
    elif export_type == 'books':
        task = export_books_to_csv.delay()
    elif export_type == 'book_requests':
        task = export_book_request_to_csv.delay()
    else:
        return jsonify({"error": "Invalid export type"}), 400  # Bad Request

    return jsonify({"task_id": task.id})


@app.get('/get-csv/<task_id>')
def get_csv(task_id):
    res = AsyncResult(task_id)
    if res.ready():
        filename = res.result
        return send_file(filename,as_attachment=True)
    else:
        return jsonify({"message":"Task Pending"}),404
    
@app.route('/api/reports/monthly')
def send_monthly_report():
    # Get the first and last day of the current month
    today = datetime.today()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # Query the database
    sections = Section.query.all()
    book_requests = BookRequest.query.filter(BookRequest.requested_date.between(first_day, last_day)).all()

    # Prepare section data
    section_data = []
    for section in sections:
        book_count = Book.query.filter_by(section_id=section.id).count()
        section_data.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'book_count': book_count
        })
    return render_template('report.html', sections=section_data, book_requests = book_requests)
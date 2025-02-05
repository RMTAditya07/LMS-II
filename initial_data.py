from datetime import datetime, time, timedelta
import os
import random
from main import app
from application.sec import datastore
from application.extensions import db
from application.api.books.models import Book
from application.api.users.models import User, Role
from application.api.sections.models import Section
from application.api.requests.models import BookRequest
from flask_security import hash_password
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    def generate_random_date(start_date, end_date):
        """Generate a random date between start_date and end_date."""
        if start_date > end_date:
            raise ValueError("start_date must be earlier than or equal to end_date")
        time_delta = end_date - start_date
        random_days = random.randint(0, time_delta.days)
        return start_date + timedelta(days=random_days)

    def focus_on_august_dates(start_date, end_date, emphasis_month=8):
        """Generate a date, focusing on August if it falls within the range."""
        # Generate a random date
        random_date = generate_random_date(start_date, end_date)
        
        # If the date is not in August, adjust it
        if random_date.month != emphasis_month:
            # If it's before August, move it to August
            if random_date.month < emphasis_month:
                random_date = random_date.replace(month=emphasis_month, day=random.randint(1, 31))
            # If it's after August, move it to August
            else:
                random_date = random_date.replace(year=random_date.year, month=emphasis_month, day=random.randint(1, 31))
        
        return random_date
    
    # Define the focus range
    focus_start_date = datetime(2024, 8, 1)
    focus_end_date = datetime(2024, 8, 6)

    # Define the general range for date generation
    general_start_date = datetime(2024, 1, 1)
    general_end_date = datetime(2024, 7, 30)
    
    default_reminder_time = time(18, 0)
    
    datastore.find_or_create_role(name="admin", description="User is an admin")
    datastore.find_or_create_role(name="student", description="User is an Student")
    db.session.commit()
    if not datastore.find_user(email = "xebosa9988@foraro.com"):
        
        datastore.create_user(username="admin",email="pamam96488@mvpalace.com", password=generate_password_hash("admin"), name="Admin", roles=["admin"], last_visit_date=generate_random_date(focus_start_date, focus_end_date),reminder_time=default_reminder_time)
    if not datastore.find_user(email = "xilope1979@eixdeal.com"):
        datastore.create_user(username="student1",email="xilope1979@eixdeal.com", password=generate_password_hash("stud1"), name="Student1",roles=["student"],reminder_time=default_reminder_time)
    if not datastore.find_user(email = "stud2@email.com"):
        datastore.create_user(username="student2",email="stud2@email.com", password=generate_password_hash("stud2"), name="Student2",roles=["student"],reminder_time=default_reminder_time)
    
    db.session.commit()
    
    sections = [
        {"name": "Science Fiction", "description": "Books that explore futuristic concepts such as advanced science and technology."},
        {"name": "Mystery", "description": "Books involving suspenseful stories that often involve solving a crime or uncovering secrets."},
        {"name": "Non-Fiction", "description": "Books that provide factual information and real-life accounts."},
        {"name": "Fantasy", "description": "Books that involve magical or supernatural elements that are not rooted in the real world."},
        {"name": "Biography", "description": "Books that tell the life story of a real person."}
    ]

    section_objects = []
    for section in sections:
        section_obj = Section(name=section["name"], description=section["description"])
        db.session.add(section_obj)
        section_objects.append(section_obj)

    db.session.commit()

    # Get all sections from the database
    sections = Section.query.all()
# Fetch users who are not admins
    users = User.query.join(User.roles).filter(Role.name != 'admin').all()
    print("Users :  ",users )
    section_ids = [section.id for section in sections]

    # Check if sections are available
    if not section_ids:
        raise ValueError("No sections found in the database.")

    # Path to the folder containing PDF files
    pdf_folder = 'books'

    # Iterate over the range of 20 books
    for i in range(1, 21):
        book_name = f"Book {i}"
        file_name = f"{i}.pdf"
        
        # Ensure the file exists
        file_path = os.path.join(pdf_folder, file_name)
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
        
        # Assign a random section to the book
        section_id = random.choice(section_ids)
        
        # Read the PDF file
        with open(file_path, 'rb') as file:
            pdf_data = file.read()
        
        # Create a new Book instance
        book = Book(
            name=book_name,
            authors=f"Author {i}",
            section_id=section_id,
            pdf_file=pdf_data,
            file_name=file_name,
            credit_cost=random.randint(1, 10),  # Random credit cost
            book_created=datetime.utcnow(),
            book_updated=datetime.utcnow()
        )
        
        # Add the book to the database
        db.session.add(book)

    # Commit the changes to the database
    db.session.commit()
    print("Books have been added successfully.")
    
    books = Book.query.all()
    
    
        # Check if books and users are available
    if not books:
        raise ValueError("No books found in the database.")
    if not users:
        raise ValueError("No users found in the database.")

    statuses = ["requested", "granted", "rejected", "returned", "revoked"]

    
    
    # Create sample book requests with different statuses
    for _ in range(30):  # Create 30 requests for demonstration
        user = random.choice(users)
        book = random.choice(books)
        status = random.choice(statuses)
        
        existing_request = BookRequest.query.filter_by(user_id=user.id, book_id=book.id).first()
        if existing_request:
            continue
        
        requested_date = generate_random_date(general_start_date, general_end_date)
        borrowed_date = generate_random_date(requested_date, general_end_date) if status in ["granted", "returned"] else None
        due_date = generate_random_date(borrowed_date, datetime(2024, 8, 30)) if borrowed_date else None
        returned_date = generate_random_date(borrowed_date, datetime(2024, 8, 30)) if status == "returned" else None
        
        # Create a new BookRequest instance
        book_request = BookRequest(
            user_id=user.id,
            book_id=book.id,
            requested_date=requested_date,
            status=status,
            feedback=f"Feedback for {book.name}" if status == "returned" else None,
            ratings=random.randint(1, 5) if status == "returned" else None,
            borrowed_date=borrowed_date,
            due_date=due_date,
            returned_date=returned_date
        )
        
        # Add the book request to the database
        db.session.add(book_request)

    # Commit the changes to the database
        db.session.commit()
    print("Book requests have been added successfully.")
from datetime import datetime, timedelta
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template_string

from application.extensions import db
from application.api.users.models import User
from application.api.requests.models import BookRequest

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'rmtaditya07@gmail.com'
SMTP_PASSWORD = 'fbtdewkmcgqaaftw'  # Ensure you securely manage this password

SENDER_EMAIL = 'rmtaditya07@gmail.com'
RECEIVER_EMAIL = 'davana2766@maxturns.com'

def generate_html_report(sections, book_requests,books):
    # Example HTML template
    html_template = """
    <html lang="en">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1, h2 {
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #ddd;
        }
    </style>
</head>
<body>
    <h1>Monthly Activity Report</h1>

    <h2>Sections</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Book Count</th>
            </tr>
        </thead>
        <tbody>
            {% for section in sections %}
            <tr>
                <td>{{ section.id }}</td>
                <td>{{ section.name }}</td>
                <td>{{ section.description }}</td>
                <td>{{ section.book_count }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <h2>Books</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Authors</th>
                <th>Request Count</th>
            </tr>
        </thead>
        <tbody>
            {% for book in books %}
            <tr>
                <td>{{ book.id }}</td>
                <td>{{ book.book_name }}</td>
                <td>{{ book.authors }}</td>
                <td>{{ book.request_count }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>Book Requests</h2>
    <table>
        <thead>
            <tr>
                <th>Request ID</th>
                <th>Book Name</th>
                <th>Section Name</th>
                <th>User Name</th>
                <th>Requested Date</th>
                <th>Status</th>
                <th>Ratings</th>
                <th>Borrowed Date</th>
                <th>Due Date</th>
                <th>Returned Date</th>
                <th>Remaining Days</th>
            </tr>
        </thead>
        <tbody>
            {% for request in book_requests %}
            <tr>
                <td>{{ request.id }}</td>
                <td>{{ request.book_name }}</td>
                <td>{{ request.section_name }}</td>
                <td>{{ request.user_name }}</td>
                <td>{{ request.requested_date }}</td>
                <td>{{ request.status }}</td>
                <td>{{ request.ratings }}</td>
                <td>{{ request.borrowed_date }}</td>
                <td>{{ request.due_date }}</td>
                <td>{{ request.returned_date }}</td>
                <td>{{ request.remaining_days }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>

    """
    return render_template_string(html_template, sections=sections, book_requests=book_requests, books=books)

def send_message(to, subject, html_content):
    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(html_content, "html"))
    
    with SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to, msg.as_string())
        
    
def send_reminders():
    now = datetime.now()
    current_time = now.time()
    
    #========================================================================================
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    print("Today : ",today)
    print("Tomorrow : ",tomorrow)
        
    # existing_request = BookRequest.query.filter_by(
    #     book_id=2,
    #     user_id=2,
    #     status="granted"
    # ).all()
    
    # for request in existing_request:
    #     db.session.delete(request)
    #     db.session.commit()

    existing_request = BookRequest.query.filter_by(
        book_id=19,
        user_id=2,
        status="granted"
    ).all()
    
    if existing_request:
        print("A granted request already exists for this user and book.")
    else : 
    # Create a new BookRequest only if no existing granted request is found
        book_request = BookRequest(
            book_id=19,
            user_id=2,
            requested_date=datetime.now(),
            borrowed_date=datetime.now(),  # Assuming the book is borrowed today
            due_date=tomorrow,
            returned_date=None,  # Not returned yet
            status="granted",  # Status 'granted'
            # ratings=None,  # Or provide a rating if required
        )
    
        # Add the new book request to the database
        db.session.add(book_request)
        db.session.commit()
        print("New book request created successfully.")

    # ==========================================================================================
    users = User.query.all()
    reminders = {}

    for user in users:
        reminder_time = user.reminder_time
        print(reminder_time)
        # if reminder_time and current_time >= reminder_time:
        print(today + timedelta(days=1))

        if reminder_time and current_time:
            # Find users with approaching due dates
            approaching_due_dates = BookRequest.query.filter(
                BookRequest.user_id == user.id,
                BookRequest.due_date <= tomorrow,
                BookRequest.returned_date.is_(None)
            ).all()
            print(approaching_due_dates)
            if approaching_due_dates:
                message = "Reminder: You have books due tomorrow. Please return them by the end of the day."
                if user.email not in reminders:
                    reminders[user.email] = []
                reminders[user.email].append(message)
            
            # Find inactive users
            if user.last_visit_date < now - timedelta(days=1):
                message = "Reminder: You haven't visited the library in a while. Please log in to stay updated."
                if user.email not in reminders:
                    reminders[user.email] = []
                reminders[user.email].append(message)
    
    # Send emails
    for email, messages in reminders.items():
        subject = "Library Reminder"
        message = "\n".join(messages)
        send_email(email, subject, message)
        
def send_email(to, subject, message):
    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(message, "plain"))
    
    with SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to, msg.as_string())
import os
import redis
import logging
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from application.extensions import db, cache, limiter
from application.api.books.models import Book
from application.api.users.models import User
from application.api.sections.models import Section
from application.api.requests.models import BookRequest
from application.sec import datastore
from application.worker import celery_init_app
from application.tasks import generate_monthly_report, send_daily_reminders
import flask_excel as excel
from celery.schedules import crontab



def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    """Factory function to create and configure the Flask application."""
    
    app = Flask(__name__,
        static_folder=os.path.join(base_dir, '..', 'static'),
        template_folder=os.path.join(base_dir, '..', 'templates'))
    app.config.from_object(DevelopmentConfig)
    
    # redis_client = redis.Redis(host='localhost', port=6379, db=0)

    
    limiter.init_app(app)
    # Initialize extensions
    db.init_app(app)
    excel.init_excel(app)
    app.security = Security(app, datastore)
    cache.init_app(app)
    
    # Register views, blueprints, or routes
    with app.app_context():
        from application.api.books import books_bp
        from application.api.books.proxy import books_bp_proxy
        
        from application.api.requests import requests_bp
        from application.api.requests.proxy import requests_bp_proxy
        
        from application.api.sections.routes_v1 import sections_bp_v1
        from application.api.sections.routes_v2 import sections_bp_v2
        from application.api.sections.proxy import sections_bp_proxy
        
        from application.api.stats import statistics_bp
        from application.api.stats.proxy import stats_bp_proxy
        
        from application.api.reports import reports_bp
        from application.api.reports.proxy import reports_bp_proxy
        
        from application.api.users import users_bp
        from application.api.users.proxy import users_bp_proxy
        
        from application.api.main import main_bp
        
        
        # Register blueprints or individual route modules
        app.register_blueprint(main_bp)
        app.register_blueprint(books_bp, url_prefix='/api/v1/books')
        app.register_blueprint(books_bp_proxy)   
        
        app.register_blueprint(requests_bp, url_prefix='/api/v1/requests')
        app.register_blueprint(requests_bp_proxy)   
         # ✅ Both v1 & v2 are now available
        app.register_blueprint(sections_bp_v1, url_prefix='/api/v1/sections')
        app.register_blueprint(sections_bp_v2, url_prefix='/api/v2/sections')
        # Register the proxy route
        app.register_blueprint(sections_bp_proxy)                      
        
        app.register_blueprint(statistics_bp, url_prefix='/api/v1/stats')
        app.register_blueprint(stats_bp_proxy)   
        
        app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
        app.register_blueprint(reports_bp_proxy)   
        
        app.register_blueprint(users_bp,url_prefix="/api/v1/user")
        app.register_blueprint(users_bp_proxy)   
    
    return app


def create_celery(app):
    """Initialize Celery with Flask app context and configure periodic tasks."""
    celery = celery_init_app(app)
    celery.conf.timezone = 'UTC'
    celery.conf.update(
        beat_schedule_filename='celerybeat-schedule',
        beat_schedule_persistence='json'
    )
    
    # Define periodic tasks
    @celery.on_after_configure.connect
    def setup_periodic_tasks(sender, **kwargs):
        # Daily task: Send daily reminders
        sender.add_periodic_task(
            crontab(minute=0, hour='*'),  # Runs every hour
            send_daily_reminders.s(),
        )
        
        # Monthly task: Generate monthly report
        sender.add_periodic_task(
            crontab(minute=0, hour=0, day_of_month=1),  # Runs at midnight on the 1st of every month
            generate_monthly_report.s('admin@email.com', "Monthly Report"),
        )
    
    return celery


# Create Flask app and Celery app
app = create_app()
celery_app = create_celery(app)

__all__ = ['app', 'celery_app']
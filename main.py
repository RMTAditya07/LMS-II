from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from application.models import db, User, Role
from application.tasks import generate_monthly_report, send_daily_reminders
from config import DevelopmentConfig
# from application.resources import api
from application.sec import datastore
from application.worker import celery_init_app
# from application.tasks import daily_reminder
import flask_excel as excel
from celery.schedules import crontab
from application.instances import cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    # api.init_app(app)
    excel.init_excel(app)
    app.security = Security(app, datastore)
    cache.init_app(app)
    with app.app_context():
        import application.views
    
    return app

app = create_app()
celery_app = celery_init_app(app)


celery_app.conf.timezone = 'UTC'

celery_app.conf.update(
    beat_schedule_filename='celerybeat-schedule',
    beat_schedule_persistence='json'
)
@celery_app.on_after_configure.connect
def send_mail(sender, **kwargs):
    # Daily task: runs every day 
    sender.add_periodic_task(
        # crontab(minute=0, hour='*'),
        crontab('*/1'),
        send_daily_reminders.s(),
    )

    
    # Monthly task: runs on the 1st day of each month 
    sender.add_periodic_task(
        # crontab(minute=0, hour=0, day_of_month=1),
        crontab('*/1'),
        generate_monthly_report.s('admin@email.com',"Monthly Report"),
    )



if __name__ == '__main__':
    app.run(debug = True)
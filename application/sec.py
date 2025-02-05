from flask_security import SQLAlchemyUserDatastore
from .extensions import db
from application.api.users.models import User, Role


datastore = SQLAlchemyUserDatastore(db,User, Role )

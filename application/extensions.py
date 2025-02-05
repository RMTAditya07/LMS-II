from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
cache = Cache()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0"
)

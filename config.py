# import os
# from dotenv import load_dotenv
# load_dotenv()


class Config(object):
    DEBUG = False
    TESTING = False
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///../databases/development.db'
    # SECRET_KEY = "thisissecter"
    # SECURITY_PASSWORD_SALT = "thisissaltt"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # WTF_CSRF_ENABLED = False
    # SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'


class ProductionConfig(Config):
#     SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DB")
#     SECRET_KEY = os.getenv("SECRET_KEY")
#     SECURITY_PASSWORD_SALT = os.getenv("SECRET_SALT")
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SECRET_KEY = "thisissecter"
    SESSION_TYPE = 'filesystem'
    SECURITY_PASSWORD_SALT = "thisissaltt"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SMTP_SERVER : "localhost"
    SMTP_PORT = 1025
    SENDER_EMAIL = "21f1005024@ds.study.iitm.ac.in"
    SENDER_PASSWORD = ""
    CACHE_REDIS_HOST ="localhost"
    CACHE_REDIS_PORT =6379
    CACHE_REDIS_DB =3
    
    


# class TestingConfig(Config):
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///../databases/test.db'
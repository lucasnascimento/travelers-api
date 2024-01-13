import os

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
UPLOAD_FOLDER = None


def init_app(app):
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")

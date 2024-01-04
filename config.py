import os

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/travelers-api-dev"
JWT_SECRET_KEY = "0de13e756093703f9fdf1c0f45a6fc91206dc732dc12016b791838fe30664f3a"
APP_SECRET_KEY = "5c4990efccb1b1f609fda5eb7d92e8741e9779f9be5b7b99207c2f89e7abbc2a"
UPLOAD_FOLDER = None


def init_app(app):
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")

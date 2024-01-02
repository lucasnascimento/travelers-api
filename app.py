from flask import Flask
from flask_jwt_extended import JWTManager

from config import JWT_SECRET_KEY, SQLALCHEMY_DATABASE_URI, APP_SECRET_KEY
from database import db
from model.user import User
from routes.user import user_bp

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = APP_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

app.register_blueprint(user_bp)


with app.app_context():
    db.create_all()

    if not db.session.query(
        User.query.filter_by(email="email@email.com").exists()
    ).scalar():
        db.session.add(User(email="email@email.com", password="MyPassword"))
        db.session.commit()

    users = db.session.execute(db.select(User)).scalars()
    app.logger.info(users)


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

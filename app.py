from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

import config
from config import APP_SECRET_KEY, JWT_SECRET_KEY, SQLALCHEMY_DATABASE_URI
from database import db
from model.token import TokenBlocklist
from model.user import User


app = Flask(__name__)
config.init_app(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = APP_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

ACCESS_EXPIRES = timedelta(hours=1)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)


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


# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


# Register blueprints for routes
# important do not move this to the top of the file
# otherwise the config will not be loaded properly
from routes.institution import institution_bp
from routes.user import user_bp
from routes.itinerary import itinerary_bp
from routes.itineraryentry import itinerary_entry_bp
from routes.itineraryrule import itinerary_rule_bp
from routes.itineraryphoto import itinerary_photo_bp
from routes.itinerarydocument import itinerary_document_bp


app.register_blueprint(user_bp)
app.register_blueprint(institution_bp)
app.register_blueprint(itinerary_bp)
app.register_blueprint(itinerary_entry_bp)
app.register_blueprint(itinerary_rule_bp)
app.register_blueprint(itinerary_photo_bp)
app.register_blueprint(itinerary_document_bp)

with app.app_context():
    db.create_all()

    if not db.session.query(
        User.query.filter_by(email="email@email.com").exists()
    ).scalar():
        db.session.add(User(email="email@email.com", password="MyPassword"))
        db.session.commit()

    users = db.session.execute(db.select(User)).scalars()
    app.logger.info(users)

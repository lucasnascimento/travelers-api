from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade

from config import APP_SECRET_KEY, JWT_SECRET_KEY, SQLALCHEMY_DATABASE_URI
from database import db
from model.token import TokenBlocklist
from model.user import User

app = Flask(__name__)

CORS(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = APP_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"connect_timeout": 1}}
db.init_app(app)
migrate = Migrate(app, db)

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
from routes.admin.group import group_bp
from routes.admin.institution import institution_bp
from routes.admin.itinerary import itinerary_bp
from routes.admin.itinerarydocument import itinerary_document_bp
from routes.admin.itineraryentry import itinerary_entry_bp
from routes.admin.itineraryphoto import itinerary_photo_bp
from routes.admin.itineraryrule import itinerary_rule_bp
from routes.admin.booking import admin_booking_bp as admin_booking_bp
from routes.admin.user import user_bp
from routes.admin.report import admin_report_bp
from routes.public.catalog import catalog_bp
from routes.public.booking import booking_bp
from routes.public.gateway import gateway_bp

app.register_blueprint(group_bp, url_prefix="/api/admin")
app.register_blueprint(user_bp, url_prefix="/api/admin")
app.register_blueprint(institution_bp, url_prefix="/api/admin")
app.register_blueprint(itinerary_bp, url_prefix="/api/admin")
app.register_blueprint(itinerary_entry_bp, url_prefix="/api/admin")
app.register_blueprint(itinerary_rule_bp, url_prefix="/api/admin")
app.register_blueprint(itinerary_photo_bp, url_prefix="/api/admin")
app.register_blueprint(itinerary_document_bp, url_prefix="/api/admin")
app.register_blueprint(admin_booking_bp, url_prefix="/api/admin")
app.register_blueprint(admin_report_bp, url_prefix="/api/admin")
app.register_blueprint(catalog_bp, url_prefix="/api/public")
app.register_blueprint(booking_bp, url_prefix="/api/public")
app.register_blueprint(gateway_bp, url_prefix="/api/public")

with app.app_context():
    upgrade()

    user = User.query.filter_by(email="admin@localhost").first()
    if not user:
        user = User(email="admin@localhost", password="admin@2024")
        db.session.add(user)
        db.session.commit()

    user_count = User.query.count()
    app.logger.info(f"user_count={user_count}")

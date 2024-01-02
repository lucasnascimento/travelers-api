import bcrypt
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from config import JWT_SECRET_KEY, SQLALCHEMY_DATABASE_URI, APP_SECRET_KEY
from database import db
from model.user import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def check_password(password, hashed_password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


with app.app_context():
    db.create_all()

    if not db.session.query(
        User.query.filter_by(email="email@email.com").exists()
    ).scalar():
        db.session.add(
            User(email="email@email.com", hashed_password=hash_password("MyPassword"))
        )
        db.session.commit()

    users = db.session.execute(db.select(User)).scalars()
    app.logger.info(users)


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = APP_SECRET_KEY


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=username).first()

    if (user is None) or (not check_password(password, user.hashed_password)):
        return jsonify({"error": "bad_username_or_password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, current_user, jwt_required
from model.user import User

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("wrong_user_or_password"), 401

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        email=current_user.email,
    )

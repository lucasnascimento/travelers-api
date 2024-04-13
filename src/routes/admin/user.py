from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)

from model.user import User, Organization, UserOrganization
from datetime import datetime, timezone
from database import db
from model.token import TokenBlocklist

user_bp = Blueprint("user", __name__)


@user_bp.route("/create_account", methods=["POST"])
def create_account():
    # email = request.json.get("email", None)
    # password = request.json.get("password", None)

    # user = User.query.filter_by(email=email).one_or_none()
    # if user:
    #     return jsonify("email_already_taken"), 409

    # user = User(email=email, password=password)
    # db.session.add(user)
    # db.session.commit()

    # access_token = create_access_token(identity=user)
    # return jsonify(access_token=access_token)
    return jsonify("self_register_not_implemented"), 501  # Not Implemented


@user_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    org = request.json.get("organization", None)

    user = User.query.filter_by(email=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("wrong_user_or_password"), 401

    if org:
        organization = Organization.query.filter_by(domain=org).one_or_none()
        if not organization:
            return jsonify("organization_not_found"), 404

        user_organization = UserOrganization.query.filter_by(
            user_id=user.id, organization_id=organization.id
        ).one_or_none()
        if not user_organization:
            return jsonify("wrong_user_or_password"), 401

        aditional_claims = {
            "tenant": organization.id,
            "tenant_name": organization.name,
            "roles": ["tenant:admin"],  # TODO(techdebt): future RBAC needed
        }

        access_token = create_access_token(
            identity=user, additional_claims=aditional_claims
        )
        refresh_token = create_refresh_token(
            identity=user, additional_claims=aditional_claims
        )

        return jsonify(access_token=access_token, refresh_token=refresh_token)

    if user.is_superuser:
        aditional_claims = {
            "roles": ["superuser"],  # TODO(techdebt): future RBAC needed
        }
        access_token = create_access_token(
            identity=user, additional_claims=aditional_claims
        )
        refresh_token = create_refresh_token(
            identity=user, additional_claims=aditional_claims
        )

        return jsonify(access_token=access_token, refresh_token=refresh_token)

    return jsonify("wrong_user_or_password"), 401


@user_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        email=current_user.email,
    )

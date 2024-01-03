from flask import Blueprint, request, jsonify
from database import db
from model.institution import Institution

institution_bp = Blueprint("institution", __name__)


@institution_bp.route("/institution", methods=["POST"])
def create_institution():
    data = request.get_json()
    new_institution = Institution(**data)
    db.session.add(new_institution)
    db.session.commit()
    return jsonify(new_institution.to_dict()), 201


@institution_bp.route("/institution", methods=["GET"])
def get_all_institutions():
    institutions = Institution.query.filter_by(is_deleted=False).all()
    return jsonify([institution.to_dict() for institution in institutions])


@institution_bp.route("/institution/<institution_id>", methods=["GET"])
def get_institution(institution_id):
    institution = Institution.query.filter_by(
        id=institution_id, is_deleted=False
    ).first()
    if institution is None:
        return jsonify(error="not_found"), 404
    return jsonify(institution.to_dict())


@institution_bp.route("/institution/<institution_id>", methods=["PUT"])
def update_institution(institution_id):
    data = request.get_json()
    Institution.query.filter_by(id=institution_id).update(data)
    db.session.commit()
    return jsonify(success=True)


@institution_bp.route("/institution/<institution_id>", methods=["DELETE"])
def delete_institution(institution_id):
    institution = Institution.query.get(institution_id)
    if institution is None:
        return jsonify(error="not_found"), 404
    institution.is_deleted = True
    db.session.commit()
    return jsonify(success=True)

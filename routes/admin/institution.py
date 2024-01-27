import mimetypes
import os
import uuid

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from config import ENVIRONMENT
from database import db
from model.file import File
from model.institution import Institution
from routes.responses import create_error_response, create_response
from upload import upload_file

institution_bp = Blueprint("institution", __name__)


@institution_bp.route("/institution", methods=["POST"])
@jwt_required()
def create_institution():
    data = request.get_json()
    new_institution = Institution(**data)
    db.session.add(new_institution)
    db.session.commit()
    data = new_institution.to_dict()
    return create_response(data)


@institution_bp.route("/institution", methods=["GET"])
@jwt_required()
def get_all_institutions():
    institutions = Institution.query.filter_by(is_deleted=False).all()
    data = [institution.to_dict() for institution in institutions]
    return create_response(data)


@institution_bp.route("/institution/<institution_id>", methods=["GET"])
@jwt_required()
def get_institution(institution_id):
    institution = Institution.query.filter_by(
        id=institution_id, is_deleted=False
    ).first()
    if institution is None:
        return create_error_response("not_found", 404)
    data = institution.to_dict()
    return create_response(data)


@institution_bp.route("/institution/<institution_id>", methods=["PUT"])
@jwt_required()
def update_institution(institution_id):
    data = request.get_json()
    Institution.query.filter_by(id=institution_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@institution_bp.route("/institution/<institution_id>", methods=["DELETE"])
@jwt_required()
def delete_institution(institution_id):
    institution = Institution.query.get(institution_id)
    if institution is None:
        return jsonify(error="not_found"), 404
    institution.is_deleted = True
    db.session.commit()
    return create_response({"success": True})


@institution_bp.route("/institution/<institution_id>/upload_logo", methods=["POST"])
@jwt_required()
def upload_logo(institution_id):
    # Check if the post request has the file part
    if "file" not in request.files:
        return jsonify(error="no_file_part"), 400
    file = request.files["file"]

    # If the user does not select a file, the browser also
    # sends an empty part with no filename.
    if file.filename == "":
        return jsonify(error="no_file_selected"), 400

    if file:
        new_uuid = uuid.uuid4()
        filename = secure_filename(f"{new_uuid}__{file.filename}")
        mime_type = mimetypes.guess_type(filename)[0]
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        path = upload_file(file, filename)
        new_file = File(
            id=new_uuid,
            mime=mime_type,
            path=path,
            file_name=filename,
            region=ENVIRONMENT,
            size_bytes=size_bytes,
        )
        db.session.add(new_file)
        db.session.flush()
        db.session.query(Institution).filter_by(id=institution_id).update(
            {"file_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})

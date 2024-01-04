from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.institution import Institution
from config import UPLOAD_FOLDER
import mimetypes
import uuid

import os

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


@institution_bp.route("/institution/<institution_id>/upload_logo", methods=["POST"])
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
        path = os.path.join(UPLOAD_FOLDER, filename)
        new_file = File(
            id=new_uuid,
            mime=mime_type,
            path=path,
            file_name=filename,
            region="local",
            size_bytes=size_bytes,
        )
        db.session.add(new_file)
        db.session.flush()
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        db.session.query(Institution).filter_by(id=institution_id).update(
            {"file_id": str(new_file.id)}
        )
        db.session.commit()

    return jsonify(success=True)

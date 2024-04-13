import mimetypes
import os
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from config import ENVIRONMENT
from database import db
from model.file import File
from model.itinerary import Itinerary
from routes.middleware import switch_tenant_by_jwt
from routes.responses import create_error_response, create_response
from upload import upload_file

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.before_request
def before_request():
    switch_tenant_by_jwt()


@itinerary_bp.route("/itinerary", methods=["POST"])
@jwt_required()
def create_itinerary():
    data = request.get_json()
    new_itinerary = Itinerary(**data)
    db.session.add(new_itinerary)
    db.session.commit()
    data = new_itinerary.to_dict()
    return create_response(data)


@itinerary_bp.route("/itinerary", methods=["GET"])
@jwt_required()
def get_all_itineraries():
    itineraries = Itinerary.query.filter_by(is_deleted=False).all()
    data = [itinerary.to_dict() for itinerary in itineraries]
    return create_response(data)


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["GET"])
@jwt_required()
def get_itinerary(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id, is_deleted=False).first()
    if itinerary is None:
        return create_error_response("not_found", 404)
    data = itinerary.to_dict()
    return create_response(data)


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["PUT"])
@jwt_required()
def update_itinerary(itinerary_id):
    data = request.get_json()
    Itinerary.query.filter_by(id=itinerary_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["DELETE"])
@jwt_required()
def delete_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary is None:
        return jsonify(error="not_found"), 404
    itinerary.is_deleted = True
    db.session.commit()
    return create_response({"success": True})


@itinerary_bp.route("/itinerary/<itinerary_id>/upload_cover", methods=["POST"])
@jwt_required()
def upload_cover(itinerary_id):
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
        db.session.query(Itinerary).filter_by(id=itinerary_id).update(
            {"cover_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})

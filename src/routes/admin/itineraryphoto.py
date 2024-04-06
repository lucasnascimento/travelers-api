import mimetypes
import os
import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from config import ENVIRONMENT, UPLOAD_FOLDER
from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryphoto import Photo
from routes.responses import create_error_response, create_response
from upload import upload_file

itinerary_photo_bp = Blueprint("itinerary_photo", __name__)


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo", methods=["POST"])
@jwt_required()
def create_photo(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryphoto = Photo(**data)
    db.session.add(new_itineraryphoto)
    db.session.commit()
    data = new_itineraryphoto.to_dict()
    return create_response(data)


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo", methods=["GET"])
@jwt_required()
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = (
        Photo.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Photo.position)
        .all()
    )
    data = [entry.to_dict() for entry in entries]
    return create_response(data)


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo/<photo_id>", methods=["GET"])
@jwt_required()
def get_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    photo = Photo.query.filter_by(
        itinerary_id=itinerary_id, id=photo_id, is_deleted=False
    ).first()
    if photo is None:
        return create_error_response("not_found", 404)
    data = photo.to_dict()
    return create_response(data)


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo/<photo_id>", methods=["PUT"])
@jwt_required()
def update_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Photo.query.filter_by(itinerary_id=itinerary_id, id=photo_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@itinerary_photo_bp.route(
    "/itinerary/<itinerary_id>/photo/<photo_id>", methods=["DELETE"]
)
@jwt_required()
def delete_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    photo = Photo.query.get(photo_id)
    if photo is None:
        return jsonify(error="not_found"), 404
    photo.is_deleted = True
    db.session.commit()
    return create_response({"success": True})


@itinerary_photo_bp.route(
    "/itinerary/<itinerary_id>/photo/<photo_id>/upload", methods=["POST"]
)
@jwt_required()
def upload_file(itinerary_id, photo_id):
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
        db.session.query(Photo).filter_by(id=photo_id).update(
            {"photo_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})

import mimetypes
import os
import uuid

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER
from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryphoto import Photo

itinerary_photo_bp = Blueprint("itinerary_photo", __name__)


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo", methods=["POST"])
def create_photo(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryphoto = Photo(**data)
    db.session.add(new_itineraryphoto)
    db.session.commit()
    return jsonify(new_itineraryphoto.to_dict()), 201


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo", methods=["GET"])
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = Photo.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    return jsonify([photo.to_dict() for photo in entries])


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo/<photo_id>", methods=["GET"])
def get_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    photo = Photo.query.filter_by(
        itinerary_id=itinerary_id, id=photo_id, is_deleted=False
    ).first()
    if photo is None:
        return jsonify(error="not_found"), 404
    return jsonify(photo.to_dict())


@itinerary_photo_bp.route("/itinerary/<itinerary_id>/photo/<photo_id>", methods=["PUT"])
def update_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Photo.query.filter_by(itinerary_id=itinerary_id, id=photo_id).update(data)
    db.session.commit()
    return jsonify(success=True)


@itinerary_photo_bp.route(
    "/itinerary/<itinerary_id>/photo/<photo_id>", methods=["DELETE"]
)
def delete_itinerary(itinerary_id, photo_id):
    Itinerary.query.get_or_404(itinerary_id)
    photo = Photo.query.get(photo_id)
    if photo is None:
        return jsonify(error="not_found"), 404
    photo.is_deleted = True
    db.session.commit()
    return jsonify(success=True)


@itinerary_photo_bp.route(
    "/itinerary/<itinerary_id>/photo/<photo_id>/upload", methods=["POST"]
)
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
        db.session.query(Photo).filter_by(id=photo_id).update(
            {"photo_id": str(new_file.id)}
        )
        db.session.commit()

    return jsonify(success=True)

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.itinerary import Itinerary
from config import UPLOAD_FOLDER
import mimetypes
import uuid

import os

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/itinerary", methods=["POST"])
def create_itinerary():
    data = request.get_json()
    new_itinerary = Itinerary(**data)
    db.session.add(new_itinerary)
    db.session.commit()
    return jsonify(new_itinerary.to_dict()), 201


@itinerary_bp.route("/itinerary", methods=["GET"])
def get_all_itineraries():
    itineraries = Itinerary.query.filter_by(is_deleted=False).all()
    return jsonify([itinerary.to_dict() for itinerary in itineraries])


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["GET"])
def get_itinerary(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id, is_deleted=False).first()
    if itinerary is None:
        return jsonify(error="not_found"), 404
    return jsonify(itinerary.to_dict())


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["PUT"])
def update_itinerary(itinerary_id):
    data = request.get_json()
    Itinerary.query.filter_by(id=itinerary_id).update(data)
    db.session.commit()
    return jsonify(success=True)


@itinerary_bp.route("/itinerary/<itinerary_id>", methods=["DELETE"])
def delete_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary is None:
        return jsonify(error="not_found"), 404
    itinerary.is_deleted = True
    db.session.commit()
    return jsonify(success=True)


@itinerary_bp.route("/itinerary/<itinerary_id>/upload_cover", methods=["POST"])
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
        db.session.query(Itinerary).filter_by(id=itinerary_id).update(
            {"cover_id": str(new_file.id)}
        )
        db.session.commit()

    return jsonify(success=True)

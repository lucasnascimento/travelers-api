from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from config import ENVIRONMENT
from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryphoto import Photo
from routes.responses import create_error_response, create_response

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
        new_file = File.create_and_upload(file, ENVIRONMENT)
        db.session.query(Photo).filter_by(id=photo_id).update(
            {"photo_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})

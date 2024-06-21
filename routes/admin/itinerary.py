from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from config import ENVIRONMENT
from database import db
from model.file import File
from model.itinerary import Itinerary
from routes.responses import create_error_response, create_response

itinerary_bp = Blueprint("itinerary", __name__)


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
        new_file = File.create_and_upload(file, ENVIRONMENT)
        db.session.query(Itinerary).filter_by(id=itinerary_id).update(
            {"cover_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})


@itinerary_bp.route("/itinerary/<itinerary_id>/upload_cover_small", methods=["POST"])
@jwt_required()
def upload_cover_small(itinerary_id):
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
        db.session.query(Itinerary).filter_by(id=itinerary_id).update(
            {"cover_small_id": str(new_file.id)}
        )
        db.session.commit()

    return create_response({"success": True})

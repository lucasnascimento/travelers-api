from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryentry import Entry
from routes.middleware import switch_tenant_by_jwt
from routes.responses import create_error_response, create_response

itinerary_entry_bp = Blueprint("itinerary_entry", __name__)


@itinerary_entry_bp.before_request
def before_request():
    switch_tenant_by_jwt()


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry", methods=["POST"])
@jwt_required()
def create_entry(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryentry = Entry(**data)
    db.session.add(new_itineraryentry)
    db.session.commit()
    data = new_itineraryentry.to_dict()
    return create_response(data)


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry", methods=["GET"])
@jwt_required()
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = (
        Entry.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Entry.position)
        .all()
    )
    data = [entry.to_dict() for entry in entries]
    return create_response(data)


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry/<entry_id>", methods=["GET"])
@jwt_required()
def get_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    entry = Entry.query.filter_by(
        itinerary_id=itinerary_id, id=entry_id, is_deleted=False
    ).first()
    if entry is None:
        return create_error_response("not_found", 404)
    data = entry.to_dict()
    return create_response(data)


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry/<entry_id>", methods=["PUT"])
@jwt_required()
def update_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Entry.query.filter_by(itinerary_id=itinerary_id, id=entry_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@itinerary_entry_bp.route(
    "/itinerary/<itinerary_id>/entry/<entry_id>", methods=["DELETE"]
)
@jwt_required()
def delete_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    entry = Entry.query.get(entry_id)
    if entry is None:
        return jsonify(error="not_found"), 404
    entry.is_deleted = True
    db.session.commit()
    return create_response({"success": True})

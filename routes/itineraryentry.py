from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryentry import Entry

itinerary_entry_bp = Blueprint("itinerary_entry", __name__)


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry", methods=["POST"])
def create_entry(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryentry = Entry(**data)
    db.session.add(new_itineraryentry)
    db.session.commit()
    return jsonify(new_itineraryentry.to_dict()), 201


@itinerary_entry_bp.route("/itinerary/<itinerary_id>/entry", methods=["GET"])
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = Entry.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    return jsonify([entry.to_dict() for entry in entries])


@itinerary_entry_bp.route(
    "/itinerary/<itinerary_id>/entry/<entry_id>", methods=["GET"]
)
def get_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    entry = Entry.query.filter_by(
        itinerary_id=itinerary_id, id=entry_id, is_deleted=False
    ).first()
    if entry is None:
        return jsonify(error="not_found"), 404
    return jsonify(entry.to_dict())


@itinerary_entry_bp.route(
    "/itinerary/<itinerary_id>/entry/<entry_id>", methods=["PUT"]
)
def update_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Entry.query.filter_by(itinerary_id=itinerary_id, id=entry_id).update(data)
    db.session.commit()
    return jsonify(success=True)


@itinerary_entry_bp.route(
    "/itinerary/<itinerary_id>/entry/<entry_id>", methods=["DELETE"]
)
def delete_itinerary(itinerary_id, entry_id):
    Itinerary.query.get_or_404(itinerary_id)
    entry = Entry.query.get(entry_id)
    if entry is None:
        return jsonify(error="not_found"), 404
    entry.is_deleted = True
    db.session.commit()
    return jsonify(success=True)

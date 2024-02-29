from flask import Blueprint, jsonify

from model.institution import Institution
from model.itinerary import Itinerary
from model.itineraryentry import Entry
from model.itineraryrule import Rule
from model.itineraryphoto import Photo
from model.itinerarydocument import Document
from routes.responses import create_response, create_error_response
from flask import request
from sqlalchemy import asc, desc

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/institutions", methods=["GET"])
def list_institutions():
    institutions = (
        Institution.query.filter_by(is_deleted=False, active_on_website=True)
        .order_by(asc(Institution.ranking))
        .all()
    )
    data = [institution.to_dict() for institution in institutions]
    return create_response(data)


@catalog_bp.route("/institutions/<institution_id>", methods=["GET"])
def get_institution(institution_id):
    x_password = request.headers.get("x-password")

    if not x_password:
        return create_error_response("unauthorized", 401)

    institution = Institution.query.filter_by(
        id=institution_id, is_deleted=False
    ).first()

    if institution.password != x_password:
        return create_error_response("unauthorized", 401)

    if institution is None:
        return create_error_response("not_found", 404)

    itineraries = (
        Itinerary.query.filter_by(institution_id=institution_id, is_deleted=False)
        .order_by(Itinerary.boarding_date)
        .all()
    )

    data = institution.to_dict()
    data["itineraries"] = [itinerary.to_dict() for itinerary in itineraries]

    return create_response(data)


@catalog_bp.route("/institutions/<institution_id>/itineraries", methods=["GET"])
def list_institution_itineraries(institution_id):
    x_password = request.headers.get("x-password")

    if not x_password:
        return create_error_response("unauthorized", 401)

    institution = Institution.query.filter_by(
        id=institution_id, is_deleted=False
    ).first()

    if institution.password != x_password:
        return create_error_response("unauthorized", 401)

    itineraries = (
        Itinerary.query.filter_by(institution_id=institution_id, is_deleted=False)
        .order_by(Itinerary.boarding_date)
        .all()
    )
    data = [itinerary.to_dict() for itinerary in itineraries]
    return jsonify({"data": data})


@catalog_bp.route("/itineraries/<itinerary_id>", methods=["GET"])
def get_itinerary(itinerary_id):
    x_password = request.headers.get("x-password")

    if not x_password:
        return create_error_response("unauthorized", 401)

    itinerary = Itinerary.query.filter_by(id=itinerary_id, is_deleted=False).first()
    if itinerary is None:
        return jsonify(error="not_found"), 404

    institution = Institution.query.filter_by(
        id=itinerary.institution_id, is_deleted=False
    ).first()

    if institution.password != x_password:
        return create_error_response("unauthorized", 401)

    data = itinerary.to_dict()

    rules = (
        Rule.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Rule.position)
        .all()
    )
    rules_data = [rule.to_dict() for rule in rules]
    data["rules"] = rules_data

    entries = (
        Entry.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Entry.position)
        .all()
    )
    entries_data = [entry.to_dict() for entry in entries]
    data["entries"] = entries_data

    photos = (
        Photo.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Photo.position)
        .all()
    )
    photos_data = [photo.to_dict() for photo in photos]
    data["photos"] = photos_data

    documents = (
        Document.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Document.position)
        .all()
    )
    documents_data = [document.to_dict() for document in documents]
    data["documents"] = documents_data

    return create_response(data)

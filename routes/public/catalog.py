from flask import Blueprint, jsonify

from model.institution import Institution
from model.itinerary import Itinerary
from model.itineraryentry import Entry
from model.itineraryrule import Rule
from model.itineraryphoto import Photo
from model.itinerarydocument import Document
from routes.responses import create_response, create_error_response

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/institutions", methods=["GET"])
def list_institutions():
    institutions = Institution.query.filter_by(is_deleted=False).all()
    data = [institution.to_dict() for institution in institutions]
    return create_response(data)


@catalog_bp.route("/institutions/<institution_id>", methods=["GET"])
def get_institution(institution_id):
    institution = Institution.query.filter_by(
        id=institution_id, is_deleted=False
    ).first()
    if institution is None:
        return create_error_response("not_found", 404)

    itineraries = Itinerary.query.filter_by(
        institution_id=institution_id, is_deleted=False
    ).all()

    data = institution.to_dict()
    data["itineraries"] = [
        {
            "id": itinerary.id,
            "title": itinerary.title,
            "boarding_date": itinerary.boarding_date,
            "landing_date": itinerary.landing_date,
            "seats": itinerary.seats,
            "seat_price": itinerary.seat_price,
            "cover": itinerary.cover.path if itinerary.cover else None,
        }
        for itinerary in itineraries
    ]

    return create_response(data)


@catalog_bp.route("/institutions/<institution_id>/itineraries", methods=["GET"])
def list_institution_itineraries(institution_id):
    itineraries = Itinerary.query.filter_by(
        institution_id=institution_id, is_deleted=False
    ).all()
    data = [itinerary.to_dict() for itinerary in itineraries]
    return jsonify({"data": data})


@catalog_bp.route("/itineraries/<itinerary_id>", methods=["GET"])
def get_itinerary(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id, is_deleted=False).first()
    if itinerary is None:
        return jsonify(error="not_found"), 404

    data = itinerary.to_dict()

    rules = Rule.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    rules_data = [
        {
            "id": rule.id,
            "position": rule.position,
            "purchase_deadline": rule.purchase_deadline,
            "installments": rule.installments,
        }
        for rule in rules
    ]
    data["rules"] = rules_data

    entries = Entry.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    entries_data = [
        {
            "id": entry.id,
            "position": entry.position,
            "title": entry.title,
            "description": entry.description,
        }
        for entry in entries
    ]
    data["entries"] = entries_data

    photos = Photo.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    photos_data = [
        {
            "id": photo.id,
            "position": photo.position,
            "title": photo.title,
            "description": photo.description,
            "path": photo.photo.path if photo.photo else None,
        }
        for photo in photos
    ]
    data["photos"] = photos_data

    documents = Document.query.filter_by(
        itinerary_id=itinerary_id, is_deleted=False
    ).all()
    documents_data = [
        {
            "id": document.id,
            "position": document.position,
            "title": document.title,
            "description": document.description,
            "link": document.link,
            "path": document.document.path if document.document else None,
        }
        for document in documents
    ]
    data["documents"] = documents_data

    return create_response(data)

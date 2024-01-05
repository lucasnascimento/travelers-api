from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryrule import Rule

itinerary_rule_bp = Blueprint("itinerary_rule", __name__)


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule", methods=["POST"])
def create_rule(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryrule = Rule(**data)
    db.session.add(new_itineraryrule)
    db.session.commit()
    return jsonify(new_itineraryrule.to_dict()), 201


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule", methods=["GET"])
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = Rule.query.filter_by(itinerary_id=itinerary_id, is_deleted=False).all()
    return jsonify([rule.to_dict() for rule in entries])


@itinerary_rule_bp.route(
    "/itinerary/<itinerary_id>/rule/<rule_id>", methods=["GET"]
)
def get_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    rule = Rule.query.filter_by(
        itinerary_id=itinerary_id, id=rule_id, is_deleted=False
    ).first()
    if rule is None:
        return jsonify(error="not_found"), 404
    return jsonify(rule.to_dict())


@itinerary_rule_bp.route(
    "/itinerary/<itinerary_id>/rule/<rule_id>", methods=["PUT"]
)
def update_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Rule.query.filter_by(itinerary_id=itinerary_id, id=rule_id).update(data)
    db.session.commit()
    return jsonify(success=True)


@itinerary_rule_bp.route(
    "/itinerary/<itinerary_id>/rule/<rule_id>", methods=["DELETE"]
)
def delete_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    rule = Rule.query.get(rule_id)
    if rule is None:
        return jsonify(error="not_found"), 404
    rule.is_deleted = True
    db.session.commit()
    return jsonify(success=True)

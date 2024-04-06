from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from database import db
from model.file import File
from model.itinerary import Itinerary
from model.itineraryrule import Rule
from routes.responses import create_error_response, create_response

itinerary_rule_bp = Blueprint("itinerary_rule", __name__)


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule", methods=["POST"])
@jwt_required()
def create_rule(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    data["itinerary_id"] = itinerary_id
    new_itineraryrule = Rule(**data)
    db.session.add(new_itineraryrule)
    db.session.commit()
    data = new_itineraryrule.to_dict()
    return create_response(data)


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule", methods=["GET"])
@jwt_required()
def get_all_entries(itinerary_id):
    Itinerary.query.get_or_404(itinerary_id)
    entries = (
        Rule.query.filter_by(itinerary_id=itinerary_id, is_deleted=False)
        .order_by(Rule.position)
        .all()
    )
    data = [entry.to_dict() for entry in entries]
    return create_response(data)


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule/<rule_id>", methods=["GET"])
@jwt_required()
def get_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    rule = Rule.query.filter_by(
        itinerary_id=itinerary_id, id=rule_id, is_deleted=False
    ).first()
    if rule is None:
        return create_error_response("not_found", 404)
    data = rule.to_dict()
    return create_response(data)


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule/<rule_id>", methods=["PUT"])
@jwt_required()
def update_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    data = request.get_json()
    Rule.query.filter_by(itinerary_id=itinerary_id, id=rule_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@itinerary_rule_bp.route("/itinerary/<itinerary_id>/rule/<rule_id>", methods=["DELETE"])
@jwt_required()
def delete_itinerary(itinerary_id, rule_id):
    Itinerary.query.get_or_404(itinerary_id)
    rule = Rule.query.get(rule_id)
    if rule is None:
        return jsonify(error="not_found"), 404
    rule.is_deleted = True
    db.session.commit()
    return create_response({"success": True})

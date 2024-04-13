from flask import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import text

from database import db
from routes.middleware import switch_tenant_by_jwt
from routes.responses import create_response

admin_booking_bp = Blueprint("admin_booking", __name__)


@admin_booking_bp.before_request
def before_request():
    switch_tenant_by_jwt()


@admin_booking_bp.route("/itinerary/<itinerary_id>/booking", methods=["GET"])
@jwt_required()
def get_booking(itinerary_id):
    query = text(
        """
        SELECT b.id as booking_id,
               b.payer_name,
               b.payer_document,
               b.payer_phone,
               b.payer_email,
               bt.id as booking_traveler_id,
               bt.traveler_name,
               bt.traveler_gender,
               bt.traveler_birthdate,
               bt.traveler_extras,
               bt.total_cents,
               i.id as invoice_id,
               i.status
          FROM booking_traveler bt
         INNER JOIN booking b
            ON b.id = bt.booking_id
         INNER JOIN invoice i
            ON b.id = i.booking_id
         WHERE b.itinerary_id = :itinerary_id
           AND b.is_deleted is false
        """
    )
    results = db.session.execute(query, {"itinerary_id": itinerary_id})
    rows = results.fetchall()
    column_names = results.keys()
    results_list = [dict(zip(column_names, row)) for row in rows]
    return create_response(results_list)

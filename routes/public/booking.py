from flask import Blueprint, request
from marshmallow import Schema, ValidationError, fields

from model.booking import Booking
from model.bookingtraveler import BookingTraveler
from model.institution import Institution
from model.itinerary import Itinerary
from database import db
from routes.responses import create_error_response, create_response

booking_bp = Blueprint("booking", __name__)


class TravelerSchema(Schema):
    traveler_name = fields.Str(required=True)
    traveler_birthdate = fields.Date(required=True)
    traveler_gender = fields.Str(required=True)
    traveler_extras = fields.Raw(required=True)


class BookingSchema(Schema):
    payer_name = fields.Str(required=True)
    payer_email = fields.Email(required=True)
    payer_phone = fields.Str(required=True)
    travelers = fields.List(fields.Nested(TravelerSchema), required=True)


@booking_bp.route("/booking/itineraries/<itinerary_id>", methods=["POST"])
def create_reservation(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id, is_deleted=False).first()

    if itinerary is None:
        return create_error_response("not_found", 404)

    x_password = request.headers.get("x-password")

    if not x_password:
        return create_error_response("unauthorized", 401)

    institution = Institution.query.filter_by(
        id=itinerary.institution_id, is_deleted=False
    ).first()

    if institution.password != x_password:
        return create_error_response("unauthorized", 401)

    if institution is None:
        return create_error_response("not_found", 404)

    schema = BookingSchema()
    try:
        booking = schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(err.messages), 400

    new_booking = Booking(
        itinerary_id=itinerary_id,
        payer_name=booking["payer_name"],
        payer_email=booking["payer_email"],
        payer_phone=booking["payer_phone"],
    )
    db.session.add(new_booking)
    db.session.flush()

    for traveler in booking["travelers"]:
        new_traveler = BookingTraveler(
            booking_id=new_booking.id,
            traveler_name=traveler["traveler_name"],
            traveler_birthdate=traveler["traveler_birthdate"],
            traveler_gender=traveler["traveler_gender"],
            traveler_extras=traveler["traveler_extras"],
        )
        db.session.add(new_traveler)

    db.session.commit()

    return create_response({"booking_id": new_booking.id})

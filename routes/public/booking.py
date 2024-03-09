import json

import requests
from flask import Blueprint, request
from marshmallow import Schema, ValidationError, fields

from config import IUGU_API_TOKEN
from database import db
from model.booking import Booking
from model.bookingtraveler import BookingTraveler
from model.institution import Institution
from model.invoice import Invoice
from model.itinerary import Itinerary
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
    payer_document = fields.Str(required=True)
    payment_method = fields.Str(required=True)
    travelers = fields.List(fields.Nested(TravelerSchema), required=True)


@booking_bp.route("/booking/itineraries/<itinerary_id>", methods=["POST"])
def create_reservation(itinerary_id):
    itinerary: Itinerary = Itinerary.query.filter_by(
        id=itinerary_id, is_deleted=False
    ).first()

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

    sold_seats = itinerary.get_sold_seats()

    if sold_seats >= itinerary.seats:
        return create_error_response("sold_out", 400)

    # TODO: this is a temporary soluton once thi is duplicated code from
    # model/itinerary.py we need understand why the column_property is not
    # woking properly
    current_payment_rule = itinerary.get_current_payment_rule()
    if current_payment_rule is None:
        return create_error_response("booking_closed", 400)
    itinerary.purchase_deadline = current_payment_rule.purchase_deadline
    itinerary.seat_price = current_payment_rule.seat_price
    itinerary.installments = current_payment_rule.installments
    itinerary.pix_discount = current_payment_rule.pix_discount

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
        payer_document=booking["payer_document"],
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
            total_cents=get_cents(itinerary.seat_price),
        )
        db.session.add(new_traveler)

    data = {
        "email": booking["payer_email"],
        "due_date": itinerary.purchase_deadline.strftime("%Y-%m-%d"),
        "items": [
            {
                "description": traveler["traveler_name"],
                "quantity": 1,
                "price_cents": get_cents(itinerary.seat_price),
            }
            for traveler in booking["travelers"]
        ],
        "payer": {
            "name": booking["payer_name"],
            "email": booking["payer_email"],
            "phone": booking["payer_phone"],
            "cpf_cnpj": booking["payer_document"],
        },
        "payable_with": [booking["payment_method"]],
        "max_installments_value": itinerary.installments,
    }

    items_total_cents = sum(
        [get_cents(itinerary.seat_price) for _ in booking["travelers"]]
    )

    discount_cents = 0
    if booking["payment_method"] == "pix":
        discount_cents = int(items_total_cents * itinerary.pix_discount)
        data["discount_cents"] = discount_cents

    total_cents = items_total_cents - discount_cents

    url = f"https://api.iugu.com/v1/invoices?api_token={IUGU_API_TOKEN}"

    payload = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    invoice_iugu = response.json()

    new_invoice = Invoice(
        booking_id=new_booking.id,
        invoice_id=invoice_iugu["id"],
        status=invoice_iugu["status"],
        method=booking["payment_method"],
        due_date=invoice_iugu["due_date"],
        invoice_url=invoice_iugu["secure_url"],
        items_total_cents=items_total_cents,
        discount_cents=discount_cents,
        total_cents=total_cents,
    )
    db.session.add(new_invoice)

    # update booking with invoice id
    new_booking.invoice_id = invoice_iugu["id"]
    db.session.add(new_booking)

    db.session.commit()

    return create_response(
        {"booking_id": new_booking.id, "invoice_url": invoice_iugu["secure_url"]}
    )


def get_cents(value: float) -> int:
    return int(value * 100)

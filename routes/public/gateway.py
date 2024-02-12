from flask import Blueprint, jsonify, request

from database import db
from model.gatewayreturn import GatewayReturn
from model.invoice import Invoice
from model.invoiceevent import InvoiceEvent
from routes.responses import create_response

gateway_bp = Blueprint("gateway", __name__)


@gateway_bp.route("/gateway/callback", methods=["POST"])
def create_return():
    body = request.form.to_dict()
    gatewayreturn = GatewayReturn(
        method=request.method,
        path=request.path,
        body=body,
        headers=dict(request.headers),
    )
    db.session.add(gatewayreturn)
    db.session.commit()

    invoice_id = body["data[id]"]
    event = body["event"]
    status = body["data[status]"] if "data[status]" in body else None

    invoice = Invoice.query.filter_by(invoice_id=invoice_id).first()
    if invoice:
        invoice_event = InvoiceEvent(
            invoice_id=invoice.id,
            gatewayreturn_id=gatewayreturn.id,
            event=event,
            status=status,
        )
        db.session.add(invoice_event)

        # update invoice status
        if event == "invoice.status_changed" and status == "paid":
            invoice.status = "paid"
            db.session.add(invoice)

        db.session.commit()

    return create_response("ok")

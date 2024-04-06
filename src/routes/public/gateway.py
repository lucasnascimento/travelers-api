import requests
import re
from flask import Blueprint, request

from config import IUGU_API_TOKEN
from database import db
from model.gatewayreturn import GatewayReturn
from model.invoice import Invoice
from model.invoiceevent import InvoiceEvent
from model.invoiceinstallment import InvoiceInstallment
from routes.responses import create_response

gateway_bp = Blueprint("gateway", __name__)

events_map = {
    "invoice.status_changed": {"paid": "PAID"},
    "invoice.due": {"pending": "OVERDUE"},
    "invoice.refund": {"refunded": "REFUNDED"},
    "invoice.payment_failed": {"pending": "PAYMENT_FAILED"},
    "invoice.installation_released": {"paid": "INSTALLMENT_PAID"},
    "invoice.released": {"paid": "PAID"},
}


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
        if event in events_map and status in events_map[event]:
            invoice.status = events_map[event][status]
            db.session.add(invoice)

        updateInvoiceExtrasAndInstallments(db, invoice)

        db.session.commit()

    return create_response("ok")


def updateInvoiceExtrasAndInstallments(db, invoice):
    internal_invoice_id = invoice.id
    external_invoice_id = invoice.invoice_id
    url = f"https://api.iugu.com/v1/invoices/{external_invoice_id}?api_token={IUGU_API_TOKEN}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        return
    invoice_iugu = response.json()
    invoice_extras = {}
    if "installments" in invoice_iugu:
        invoice_extras["installments"] = invoice_iugu["installments"]
    if "credit_card_transaction" in invoice_iugu:
        invoice_extras["credit_card_transaction"] = invoice_iugu[
            "credit_card_transaction"
        ]
    if "financial_return_dates" in invoice_iugu:
        invoice_extras["financial_return_dates"] = invoice_iugu[
            "financial_return_dates"
        ]
        # upsert installments
        if invoice_iugu["financial_return_dates"] is not None:
            for installment in invoice_iugu["financial_return_dates"]:
                installment_id = installment["id"]
                invoice_installment = InvoiceInstallment.query.filter_by(
                    invoice_id=internal_invoice_id,
                    external_installment_id=str(installment_id),
                ).first()
                if not invoice_installment:
                    invoice_installment = InvoiceInstallment(
                        invoice_id=invoice.id,
                        external_installment_id=installment_id,
                        installment=(
                            installment["installment"]
                            if "installment" in installment
                            else None
                        ),
                        due_date=(
                            installment["return_date_iso"]
                            if "return_date_iso" in installment
                            else None
                        ),
                        amount_cents=(
                            installment["amount_cents"]
                            if "amount_cents" in installment
                            else None
                        ),
                        status=(
                            installment["status"] if "status" in installment else None
                        ),
                    )
                    db.session.add(invoice_installment)
                else:
                    invoice_installment.status = (
                        installment["status"] if "status" in installment else None
                    )
                    # quando há estorno, os dois campos tem valores diferentes
                    # o campo amount é o valor recalculado descontado o estorno
                    # o campo amount_cents é o valor original da parcela,
                    # então temos que atualizar o nosso campo amount com o valor já
                    # calculado da parcela considerando o estorno em centavos
                    amount = (
                        installment["amount"]
                        if "amount" in installment
                        else "0"
                    )
                    # o campo amount da iugu vem formatado como R$ 1.000,00 por exemplo.
                    amount_cents = int(re.sub("[^0-9]", "", amount))
                    invoice_installment.amount_cents = amount_cents

                    db.session.add(invoice_installment)

    version = invoice.invoice_extras if invoice.invoice_extras else {}
    if "versions" in version:
        del version["versions"]
    versions = (
        (
            invoice.invoice_extras["versions"]
            if "versions" in invoice.invoice_extras
            else []
        )
        if invoice.invoice_extras
        else []
    )
    versions.insert(0, version)
    invoice_extras["versions"] = versions

    invoice.invoice_extras = invoice_extras
    db.session.add(invoice)

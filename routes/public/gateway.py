from flask import Blueprint, jsonify, request

from database import db
from model.gatewayreturn import GatewayReturn
from routes.responses import create_response

gateway_bp = Blueprint("gateway", __name__)


@gateway_bp.route("/gateway/callback", methods=["POST"])
def create_return():
    body = request.form.to_dict()
    data = GatewayReturn(
        method=request.method,
        path=request.path,
        body=body,
        headers=dict(request.headers),
    )
    db.session.add(data)
    db.session.commit()

    return create_response("ok")

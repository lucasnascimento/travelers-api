from flask import Blueprint, jsonify, request

from database import db
from model.gatewayreturn import GatewayReturn
from routes.responses import create_response

gateway_bp = Blueprint("gateway", __name__)


@gateway_bp.route("/gateway/callback", methods=["GET", "POST"])
def create_return():
    data = GatewayReturn(
        method=request.method,
        path=request.path,
        body=request.get_json(),
        headers=dict(request.headers),
    )
    db.session.add(data)
    db.session.commit()

    return create_response("ok")

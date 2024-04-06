import mimetypes
import os
import uuid

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from config import ENVIRONMENT
from database import db
from model.file import File
from model.group import Group
from routes.responses import create_error_response, create_response
from upload import upload_file

group_bp = Blueprint("group", __name__)


@group_bp.route("/group", methods=["POST"])
@jwt_required()
def create_group():
    data = request.get_json()
    new_group = Group(**data)
    db.session.add(new_group)
    db.session.commit()
    data = new_group.to_dict()
    return create_response(data)


@group_bp.route("/group", methods=["GET"])
@jwt_required()
def get_all_groups():
    groups = Group.query.filter_by(is_deleted=False).all()
    data = [group.to_dict() for group in groups]
    return create_response(data)


@group_bp.route("/group/<group_id>", methods=["GET"])
@jwt_required()
def get_group(group_id):
    group = Group.query.filter_by(id=group_id, is_deleted=False).first()
    if group is None:
        return create_error_response("not_found", 404)
    data = group.to_dict()
    return create_response(data)


@group_bp.route("/group/<group_id>", methods=["PUT"])
@jwt_required()
def update_group(group_id):
    data = request.get_json()
    Group.query.filter_by(id=group_id).update(data)
    db.session.commit()
    return create_response({"success": True})


@group_bp.route("/group/<group_id>", methods=["DELETE"])
@jwt_required()
def delete_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        return jsonify(error="not_found"), 404
    group.is_deleted = True
    db.session.commit()
    return create_response({"success": True})

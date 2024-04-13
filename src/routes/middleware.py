from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask import request
from model.user import UserOrganization, Organization
from database import Database
from urllib.parse import urlparse


def switch_tenant_by_jwt():
    """Before request

    switch tenant schema
    """
    verify_jwt_in_request()

    # tenant is the organization_id
    tenant = get_jwt().get("tenant")
    if not tenant:
        return {"message": "You are not logged into any tenant"}, 403

    user = get_jwt_identity()

    organization = Organization.query.filter_by(id=tenant).first()

    if not UserOrganization.query.filter_by(
        user_id=user, organization_id=tenant
    ).first():
        return {"message": "You are not a member of this tenant"}, 403

    Database(organization.schema).switch_schema()


def switch_tenant_not_logged_requests():
    parsed_url = urlparse(request.host_url)
    host = parsed_url.hostname
    parts = host.split(".")
    schema = next(iter(parts), None)  # get the first element of the endpoint

    organization = Organization.query.filter_by(schema=schema).one_or_none()
    if organization:
        Database(schema).switch_schema()
    else:
        # keep on public schema
        pass

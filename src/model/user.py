import uuid
from datetime import datetime

import bcrypt
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class User(db.Model):
    __table_name__ = "user"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(db.String, nullable=False)
    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, email, password) -> None:
        super().__init__()
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        password_bytes = password.encode("utf-8")
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.hashed_password = hashed_bytes.decode("utf-8")

    def check_password(self, password):
        password_bytes = password.encode("utf-8")
        hashed_bytes = self.hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)


class Organization(db.Model):
    __table_name__ = "organization"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    schema: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, name, schema, domain) -> None:
        super().__init__()
        self.name = name
        self.schema = schema
        self.domain = domain


class UserOrganization(db.Model):
    __table_name__ = "user_organization"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("user.id"), primary_key=True
    )
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("organization.id"), primary_key=True
    )

    inserted_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[str] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, user_id, organization_id) -> None:
        super().__init__()
        self.user_id = user_id
        self.organization_id = organization_id
